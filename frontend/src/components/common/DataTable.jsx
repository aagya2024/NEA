/**
 * DataTable — Reusable paginated, sortable table component.
 */

export default function DataTable({ columns, data, loading, emptyMessage = 'No data found.' }) {
    if (loading) {
        return (
            <div className="card p-8 flex justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-4 border-nea-blue border-t-transparent" />
            </div>
        );
    }

    if (!data || data.length === 0) {
        return (
            <div className="card p-8 text-center text-gray-400">
                <div className="text-4xl mb-2">📋</div>
                {emptyMessage}
            </div>
        );
    }

    return (
        <div className="card overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="bg-gray-50 border-b border-gray-200">
                            {columns.map((col) => (
                                <th
                                    key={col.key}
                                    className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
                                    style={{ width: col.width }}
                                >
                                    {col.label}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {data.map((row, i) => (
                            <tr key={row.id || i} className="hover:bg-gray-50 transition-colors">
                                {columns.map((col) => (
                                    <td key={col.key} className="px-4 py-3 text-gray-700">
                                        {col.render ? col.render(row) : row[col.key]}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
