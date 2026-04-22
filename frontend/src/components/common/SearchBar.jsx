/**
 * SearchBar — Debounced search input.
 */

import { useState, useEffect } from 'react';
import { FiSearch, FiX } from 'react-icons/fi';

export default function SearchBar({ value = '', onChange, placeholder = 'Search...', delay = 400 }) {
    const [local, setLocal] = useState(value);

    useEffect(() => {
        const timer = setTimeout(() => onChange(local), delay);
        return () => clearTimeout(timer);
    }, [local, delay]);

    useEffect(() => {
        setLocal(value);
    }, [value]);

    return (
        <div className="relative">
            <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
                type="text"
                value={local}
                onChange={(e) => setLocal(e.target.value)}
                placeholder={placeholder}
                className="input-field pl-10 pr-9"
            />
            {local && (
                <button
                    onClick={() => { setLocal(''); onChange(''); }}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                    <FiX className="w-4 h-4" />
                </button>
            )}
        </div>
    );
}
