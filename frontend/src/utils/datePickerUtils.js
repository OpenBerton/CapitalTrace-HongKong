export function parseIsoDate(value) {
  if (!value) {
    return null;
  }
  const [year, month, day] = value.split("-").map(Number);
  if (!year || !month || !day) {
    return null;
  }
  return new Date(year, month - 1, day);
}

export function formatIsoDate(dateObj) {
  const year = dateObj.getFullYear();
  const month = String(dateObj.getMonth() + 1).padStart(2, "0");
  const day = String(dateObj.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function toSelectableDates(tradingDays) {
  return tradingDays
    .map((tradingDay) => parseIsoDate(tradingDay))
    .filter((item) => item);
}

export function buildIsoDateSet(dates) {
  return new Set(dates.map((item) => formatIsoDate(item)));
}
