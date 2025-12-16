/**
 * Terminal Animation & Effects
 * Adds subtle terminal-like effects to the security blog
 */

(function() {
  'use strict';

  // Initialize terminal effects on page load
  document.addEventListener('DOMContentLoaded', function() {
    initTerminalEffects();
    initTypewriterEffect();
    addGlitchEffect();
  });

  /**
   * Initialize terminal-like effects
   */
  function initTerminalEffects() {
    // Add scan line effect
    const scanlines = document.createElement('div');
    scanlines.className = 'scanlines';
    scanlines.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 9999;
      background: repeating-linear-gradient(
        0deg,
        rgba(0, 0, 0, 0.03),
        rgba(0, 0, 0, 0.03) 2px,
        transparent 2px,
        transparent 4px
      );
      animation: flicker 0.15s infinite;
    `;
    document.body.appendChild(scanlines);

    // Add flicker animation to style
    if (!document.getElementById('terminal-animations')) {
      const style = document.createElement('style');
      style.id = 'terminal-animations';
      style.textContent = `
        @keyframes flicker {
          0% { opacity: 0.97; }
          50% { opacity: 1; }
          100% { opacity: 0.97; }
        }

        @keyframes glitch {
          0% { transform: translateX(0); }
          20% { transform: translateX(-2px); }
          40% { transform: translateX(2px); }
          60% { transform: translateX(-2px); }
          80% { transform: translateX(2px); }
          100% { transform: translateX(0); }
        }

        .glitch-effect {
          animation: glitch 0.3s ease-in-out;
        }
      `;
      document.head.appendChild(style);
    }
  }

  /**
   * Add typewriter effect to terminal headers
   */
  function initTypewriterEffect() {
    const headers = document.querySelectorAll('.terminal-header');
    headers.forEach(header => {
      const pathElement = header.querySelector('.terminal-path');
      if (pathElement) {
        const text = pathElement.textContent;
        pathElement.textContent = '';
        let index = 0;

        function typeCharacter() {
          if (index < text.length) {
            pathElement.textContent += text[index];
            index++;
            setTimeout(typeCharacter, 50);
          }
        }

        // Start typewriter effect when element is visible
        if (isElementInViewport(header)) {
          typeCharacter();
        } else {
          const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
              if (entry.isIntersecting && index === 0) {
                typeCharacter();
                observer.unobserve(entry.target);
              }
            });
          });
          observer.observe(header);
        }
      }
    });
  }

  /**
   * Add glitch effect on hover for links
   */
  function addGlitchEffect() {
    const links = document.querySelectorAll('a');
    links.forEach(link => {
      link.addEventListener('mouseenter', function() {
        if (Math.random() > 0.7) { // 30% chance for glitch effect
          this.classList.add('glitch-effect');
          setTimeout(() => {
            this.classList.remove('glitch-effect');
          }, 300);
        }
      });
    });
  }

  /**
   * Check if element is in viewport
   */
  function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
  }

  /**
   * Matrix rain effect for hero sections (optional enhancement)
   */
  window.startMatrixRain = function(containerId, duration = 3000) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
    const containerWidth = container.offsetWidth;
    const containerHeight = container.offsetHeight;

    function createRain() {
      const rain = document.createElement('div');
      rain.style.cssText = `
        position: absolute;
        color: #00ff00;
        opacity: 0.5;
        font-family: monospace;
        font-size: 12px;
        text-shadow: 0 0 5px #00ff00;
      `;

      rain.textContent = chars[Math.floor(Math.random() * chars.length)];
      rain.style.left = Math.random() * containerWidth + 'px';
      rain.style.top = '-20px';

      container.appendChild(rain);

      let top = -20;
      const speed = Math.random() * 2 + 1;
      const animation = setInterval(() => {
        top += speed;
        rain.style.top = top + 'px';

        if (top > containerHeight) {
          clearInterval(animation);
          rain.remove();
        }
      }, 30);
    }

    const rainInterval = setInterval(createRain, 100);
    setTimeout(() => clearInterval(rainInterval), duration);
  };

  /**
   * CRT monitor effect (advanced styling)
   */
  window.enableCRTEffect = function(enable = true) {
    const style = document.getElementById('terminal-animations');
    if (!style) return;

    if (enable) {
      style.textContent += `
        body {
          filter: contrast(1.1) saturate(0.8);
        }
        body::before {
          content: '';
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: radial-gradient(ellipse at center, transparent 0%, rgba(0,0,0,0.2) 100%);
          pointer-events: none;
          z-index: 9998;
        }
      `;
    }
  };

  /**
   * Add scroll-to-top button with terminal style
   */
  window.addScrollToTop = function() {
    const button = document.createElement('button');
    button.innerHTML = '↑ root@phucquan';
    button.style.cssText = `
      position: fixed;
      bottom: 30px;
      right: 30px;
      background: rgba(0, 255, 0, 0.1);
      color: #00ff00;
      border: 2px solid #00ff00;
      padding: 10px 20px;
      border-radius: 3px;
      cursor: pointer;
      font-family: monospace;
      font-size: 12px;
      display: none;
      z-index: 999;
      transition: all 0.3s;
      text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
    `;

    button.addEventListener('mouseenter', function() {
      this.style.boxShadow = '0 0 10px rgba(0, 255, 0, 0.5)';
      this.style.textShadow = '0 0 15px rgba(0, 255, 0, 0.8)';
    });

    button.addEventListener('mouseleave', function() {
      this.style.boxShadow = 'none';
      this.style.textShadow = '0 0 10px rgba(0, 255, 0, 0.5)';
    });

    button.addEventListener('click', function() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    document.body.appendChild(button);

    window.addEventListener('scroll', function() {
      if (window.pageYOffset > 300) {
        button.style.display = 'block';
      } else {
        button.style.display = 'none';
      }
    });
  };

})();

// Optional: Call optional features
// startMatrixRain('hero-section', 2000);
// enableCRTEffect(false); // Disabled by default
// addScrollToTop();
