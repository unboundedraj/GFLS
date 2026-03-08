import * as XLSX from "xlsx";

export function readExcelClientSide(file, sheetName = "Sheet1") {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = e => {
      try {
        const wb = XLSX.read(e.target.result, { type: "array" });
        const sName = wb.SheetNames.includes(sheetName) ? sheetName : wb.SheetNames[0];
        const ws = wb.Sheets[sName];
        const raw = XLSX.utils.sheet_to_json(ws, { defval: null });
        const columns = raw.length > 0 ? Object.keys(raw[0]) : [];
        resolve({
          columns,
          preview: raw.slice(0, 10),
          totalRows: raw.length,
          totalCols: columns.length,
          sheetNames: wb.SheetNames,
          usedSheet: sName,
        });
      } catch (err) {
        reject(err);
      }
    };
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });
}
