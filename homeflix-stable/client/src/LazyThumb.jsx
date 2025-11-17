import { useEffect, useRef, useState } from "react";

export default function LazyThumb({ src, alt = "", className = "", rootMargin = "200px", ...rest }) {
  const [visible, setVisible] = useState(false);
  const imgRef = useRef(null);

  useEffect(() => {
    if (!imgRef.current) return;

    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              setVisible(true);
              observer.disconnect();
            }
          });
        },
        { root: null, rootMargin, threshold: 0.01 }
      );
      observer.observe(imgRef.current);
      return () => observer.disconnect();
    } else {
      // Fallback anciens navigateurs
      setVisible(true);
    }
  }, [rootMargin]);

  return (
    <img
      ref={imgRef}
      className={className}
      src={visible ? src : undefined}
      data-src={src}
      alt={alt}
      loading="lazy"
      decoding="async"
      {...rest}
    />
  );
}

