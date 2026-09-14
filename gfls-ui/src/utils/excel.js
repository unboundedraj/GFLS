export async function readExcelClientSide(file, sheetName = "Sheet1") {
  // SheetJS is large, so it is only loaded once an Excel file is actually picked
  const XLSX = await import("xlsx");
  const buffer = await file.arrayBuffer();

  const wb = XLSX.read(buffer, { type: "array" });
  const sName = wb.SheetNames.includes(sheetName) ? sheetName : wb.SheetNames[0];
  const ws = wb.Sheets[sName];
  const raw = XLSX.utils.sheet_to_json(ws, { defval: null });
  const columns = raw.length > 0 ? Object.keys(raw[0]) : [];
  return {
    columns,
    preview: raw.slice(0, 10),
    totalRows: raw.length,
    totalCols: columns.length,
    sheetNames: wb.SheetNames,
    usedSheet: sName,
  };
}
