import { useEffect, useMemo, useRef, useState } from "react";

function buildRowId(item, index) {
  return `${index}:${item.name || "-"}`;
}

export default function useParticipantSelection(participants) {
  const selectableIds = useMemo(
    () => participants.map((item, index) => buildRowId(item, index)),
    [participants],
  );

  const [selectedParticipants, setSelectedParticipants] = useState(new Set());
  const selectAllRef = useRef(null);

  useEffect(() => {
    setSelectedParticipants(new Set(selectableIds));
  }, [selectableIds]);

  const selectedCount = selectedParticipants.size;
  const totalCount = selectableIds.length;
  const isAllSelected = totalCount > 0 && selectedCount === totalCount;
  const isPartiallySelected = selectedCount > 0 && selectedCount < totalCount;

  useEffect(() => {
    if (!selectAllRef.current) {
      return;
    }
    selectAllRef.current.indeterminate = isPartiallySelected;
  }, [isPartiallySelected]);

  const selectedTotals = useMemo(() => {
    return participants.reduce(
      (acc, item, index) => {
        const rowId = buildRowId(item, index);
        if (!selectedParticipants.has(rowId)) {
          return acc;
        }

        const ratio = Number(item.percentage || 0);
        acc.totalSelectedRatio += Number.isFinite(ratio) ? ratio : 0;

        if (item.deltaShares == null) {
          return acc;
        }

        const delta = Number(item.deltaShares);
        if (Number.isFinite(delta)) {
          acc.totalNetFlow += delta;
        }
        return acc;
      },
      {
        totalNetFlow: 0,
        totalSelectedRatio: 0,
      },
    );
  }, [participants, selectedParticipants]);

  const netFlowClass =
    selectedTotals.totalNetFlow > 0
      ? "text-emerald-600 bg-emerald-50"
      : selectedTotals.totalNetFlow < 0
      ? "text-red-600 bg-red-50"
      : "text-slate-700 bg-slate-100";

  const toggleParticipant = (rowId) => {
    setSelectedParticipants((prev) => {
      const next = new Set(prev);
      if (next.has(rowId)) {
        next.delete(rowId);
      } else {
        next.add(rowId);
      }
      return next;
    });
  };

  const handleToggleAll = () => {
    if (isAllSelected) {
      setSelectedParticipants(new Set());
      return;
    }
    setSelectedParticipants(new Set(selectableIds));
  };

  return {
    buildRowId,
    selectedParticipants,
    selectedCount,
    totalCount,
    isAllSelected,
    selectedTotals,
    netFlowClass,
    selectAllRef,
    toggleParticipant,
    handleToggleAll,
  };
}
