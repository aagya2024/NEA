/**
 * Footer
 * ======
 * Government-style footer with NEA info.
 */

export default function Footer() {
    return (
        <footer className="bg-white border-t border-gray-200 px-6 py-4">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-gray-400">
                <span>© {new Date().getFullYear()} Nepal Electricity Authority. Internal use only.</span>
                <span>NEA Intranet Portal v1.0.0</span>
            </div>
        </footer>
    );
}
