export function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString("zh-Hant", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}
