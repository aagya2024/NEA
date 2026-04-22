/**
 * FileUpload — Drag-and-drop file upload component.
 */

import { useState, useRef } from 'react';
import { FiUploadCloud, FiFile, FiX } from 'react-icons/fi';

export default function FileUpload({ accept, onFileSelect, label = 'Upload file', maxSizeMB = 50 }) {
    const [dragActive, setDragActive] = useState(false);
    const [file, setFile] = useState(null);
    const [error, setError] = useState('');
    const inputRef = useRef(null);

    const handleFile = (f) => {
        setError('');
        if (f.size > maxSizeMB * 1024 * 1024) {
            setError(`File too large. Max size: ${maxSizeMB}MB`);
            return;
        }
        setFile(f);
        onFileSelect?.(f);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragActive(false);
        if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]);
    };

    const handleChange = (e) => {
        if (e.target.files?.[0]) handleFile(e.target.files[0]);
    };

    const clear = () => {
        setFile(null);
        setError('');
        onFileSelect?.(null);
        if (inputRef.current) inputRef.current.value = '';
    };

    return (
        <div>
            <div
                className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${dragActive ? 'border-nea-blue bg-blue-50' : 'border-gray-300 hover:border-gray-400'
                    }`}
                onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
                onDragLeave={() => setDragActive(false)}
                onDrop={handleDrop}
                onClick={() => inputRef.current?.click()}
            >
                <input
                    ref={inputRef}
                    type="file"
                    accept={accept}
                    onChange={handleChange}
                    className="hidden"
                />

                {file ? (
                    <div className="flex items-center justify-center gap-3">
                        <FiFile className="w-6 h-6 text-nea-blue" />
                        <span className="text-sm font-medium text-gray-700">{file.name}</span>
                        <button
                            onClick={(e) => { e.stopPropagation(); clear(); }}
                            className="p-1 rounded-full hover:bg-gray-200"
                        >
                            <FiX className="w-4 h-4 text-gray-500" />
                        </button>
                    </div>
                ) : (
                    <>
                        <FiUploadCloud className="w-10 h-10 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm text-gray-500">{label}</p>
                        <p className="text-xs text-gray-400 mt-1">Drag & drop or click to browse</p>
                    </>
                )}
            </div>
            {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
        </div>
    );
}
