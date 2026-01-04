import { useEffect, useRef, useState } from "react";

/**
 * Custom hook for autosaving content with debounce
 * @param {Function} saveFunction - Async function to call for saving
 * @param {any} content - Content to save
 * @param {number} delay - Debounce delay in milliseconds (default: 2000)
 */
export function useAutosave(saveFunction, content, delay = 2000) {
  const [status, setStatus] = useState("idle"); // idle, saving, saved, error
  const [error, setError] = useState(null);
  const timeoutRef = useRef(null);
  const initialRenderRef = useRef(true);

  useEffect(() => {
    // Skip autosave on initial render
    if (initialRenderRef.current) {
      initialRenderRef.current = false;
      return;
    }

    // Clear previous timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set new timeout for autosave
    setStatus("idle");
    timeoutRef.current = setTimeout(async () => {
      setStatus("saving");
      setError(null);

      try {
        await saveFunction(content);
        setStatus("saved");

        // Reset to idle after 2 seconds
        setTimeout(() => {
          setStatus("idle");
        }, 2000);
      } catch (err) {
        setStatus("error");
        setError(err.response?.data?.error || "Failed to autosave");
      }
    }, delay);

    // Cleanup
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [content, delay, saveFunction]);

  return { status, error };
}
