'use client';

import { cn } from '@/lib/utils';
import React, { useRef, useState, useId } from 'react';

export interface FileUploadProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange'> {
  accept?: string;
  maxSize?: number; // in bytes
  error?: string;
  label?: string;
  helperText?: string;
  onChange?: (file: File | null) => void;
}

export function FileUpload({
  className,
  accept = '.csv',
  maxSize,
  error,
  label,
  helperText,
  id,
  onChange,
  ...props
}: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [fileError, setFileError] = useState<string | undefined>(error);
  const [fileName, setFileName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const reactId = useId();
  const uploadId = id || reactId;

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateFile = (file: File): boolean => {
    // Check file type
    if (accept && !accept.split(',').some(type => {
      if (type.startsWith('.')) {
        // Extension check
        return file.name.toLowerCase().endsWith(type.toLowerCase());
      } else {
        // MIME type check
        return file.type === type || file.type.startsWith(`${type.split('/')[0]}/`);
      }
    })) {
      setFileError(`File type not accepted. Please upload ${accept} files.`);
      return false;
    }

    // Check file size
    if (maxSize && file.size > maxSize) {
      const sizeMB = maxSize / (1024 * 1024);
      setFileError(`File is too large. Maximum size is ${sizeMB} MB.`);
      return false;
    }

    setFileError(undefined);
    return true;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (validateFile(file)) {
        setFileName(file.name);
        if (onChange) onChange(file);
      } else {
        e.target.value = '';
        setFileName(null);
        if (onChange) onChange(null);
      }
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        setFileName(file.name);
        if (onChange) onChange(file);
        // Update the input value for consistency
        if (inputRef.current) {
          // This is a hack to set the file to the input
          const dataTransfer = new DataTransfer();
          dataTransfer.items.add(file);
          inputRef.current.files = dataTransfer.files;
        }
      } else {
        if (onChange) onChange(null);
      }
    }
  };

  const handleClick = () => {
    inputRef.current?.click();
  };

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    setFileName(null);
    if (inputRef.current) inputRef.current.value = '';
    if (onChange) onChange(null);
  };

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={uploadId}
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
        >
          {label}
        </label>
      )}
      <div
        className={cn(
          'border-2 border-dashed rounded-lg p-6 text-center cursor-pointer',
          dragActive ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'border-gray-300 hover:border-primary-500',
          fileError && 'border-red-500',
          className
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          id={uploadId}
          type="file"
          ref={inputRef}
          className="hidden"
          accept={accept}
          onChange={handleChange}
          {...props}
        />
        
        {fileName ? (
          <div className="flex items-center justify-center space-x-2">
            <svg
              className="w-6 h-6 text-primary-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <span className="text-sm truncate max-w-xs">{fileName}</span>
            <button
              type="button"
              onClick={handleRemove}
              className="text-gray-500 hover:text-red-500"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        ) : (
          <div>
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Drag and drop your file here, or click to select
            </p>
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-500">
              {accept.split(',').join(', ')} files only
              {maxSize && ` (max ${(maxSize / (1024 * 1024)).toFixed(1)} MB)`}
            </p>
          </div>
        )}
      </div>
      {fileError ? (
        <p className="mt-1 text-sm text-red-500">{fileError}</p>
      ) : helperText ? (
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{helperText}</p>
      ) : null}
    </div>
  );
}