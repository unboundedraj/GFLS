import { Alert } from "./Alert";

export function DataTable({ rows, columns, emptyMsg = "No data available." }) {
  if (!rows || rows.length === 0) return <Alert type="info">{emptyMsg}</Alert>;
  const cols = columns || Object.keys(rows[0]);
  return (
    <div className="tbl-wrap">
      <table className="tbl">
        <thead>
          <tr>
            {cols.map((c) => (
              <th key={c}>{String(c)}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              {cols.map((c) => {
                const v = r[c];
                const empty = v === null || v === undefined || v === "";
                return (
                  <td key={c} className={empty ? "null" : ""}>
                    {empty ? "—" : String(v)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
