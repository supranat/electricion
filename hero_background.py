"""Reusable transformer hero background styles and canvas animation."""

HERO_BACKGROUND_CSS = """
.hero .bg-glow {
    z-index: 0;
    overflow: hidden;
    background:
        radial-gradient(ellipse 55% 45% at 90% 8%, rgba(255, 190, 0, .22) 0%,
            rgba(255, 160, 0, .08) 40%, transparent 70%),
        radial-gradient(ellipse 50% 45% at 8% 92%, rgba(255, 140, 0, .16) 0%,
            rgba(255, 120, 0, .06) 40%, transparent 70%);
}

.hero .bg-glow::before,
.hero .bg-glow::after {
    content: "";
    position: absolute;
    width: clamp(190px, 32vw, 420px);
    aspect-ratio: 1;
    border-radius: 50%;
    filter: blur(58px);
    opacity: .28;
    background: #ffd400;
    animation: heroGlowDrift 11s ease-in-out infinite alternate;
}

.hero .bg-glow::before { top: -35%; left: 10%; }
.hero .bg-glow::after {
    right: 5%;
    bottom: -48%;
    background: #ff8c00;
    animation-delay: -5s;
}

.hero .bg-grid {
    z-index: 1;
    background-image:
        linear-gradient(rgba(255, 200, 0, .16) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 200, 0, .16) 1px, transparent 1px),
        linear-gradient(rgba(255, 200, 0, .07) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 200, 0, .07) 1px, transparent 1px);
    background-size: 240px 240px, 240px 240px, 48px 48px, 48px 48px;
    -webkit-mask-image: radial-gradient(ellipse 70% 65% at 50% 50%,
        #000 20%, transparent 100%);
    mask-image: radial-gradient(ellipse 70% 65% at 50% 50%,
        #000 20%, transparent 100%);
}

.hero .bg-network {
    z-index: 2;
    -webkit-mask-image: radial-gradient(ellipse 45% 40% at 50% 38%,
        transparent 30%, #000 100%);
    mask-image: radial-gradient(ellipse 45% 40% at 50% 38%,
        transparent 30%, #000 100%);
}

.hero .bg-spotlight {
    z-index: 3;
    background: radial-gradient(ellipse 38% 34% at 50% 82%,
        rgba(255, 170, 0, .38) 0%, rgba(255, 130, 0, .18) 35%,
        rgba(255, 110, 0, .05) 60%, transparent 75%);
    mix-blend-mode: screen;
    animation: heroSpotlightPulse 6s ease-in-out infinite;
}

.hero .bg-scanline {
    z-index: 4;
    overflow: hidden;
}

.hero .scan-line {
    position: absolute;
    left: 0;
    right: 0;
    top: 78%;
    height: 1px;
    overflow: hidden;
    background: linear-gradient(90deg, transparent 0%,
        rgba(255, 190, 0, .55) 25%, rgba(255, 220, 90, .9) 50%,
        rgba(255, 190, 0, .55) 75%, transparent 100%);
    box-shadow: 0 0 12px rgba(255, 190, 0, .5);
}

.hero .scan-line::after {
    content: "";
    position: absolute;
    top: -1px;
    left: -20%;
    width: 20%;
    height: 3px;
    background: linear-gradient(90deg, transparent, rgba(255, 245, 190, 1), transparent);
    filter: blur(1px);
    animation: scanMove 5s ease-in-out infinite;
}

.hero .bg-vignette {
    z-index: 5;
    background: radial-gradient(ellipse 85% 75% at 50% 45%,
        transparent 55%, rgba(0, 0, 0, .55) 100%);
}

.hero .hero-content,
.hero .stage { position: relative; z-index: 6; }
.hero-content { max-width: 850px; }
.hero .ring {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 82%;
    aspect-ratio: 1;
    border: 2px solid rgba(255, 212, 0, .18);
    border-top-color: rgba(255, 245, 190, .95);
    border-right-color: rgba(255, 170, 0, .75);
    border-radius: 50%;
    box-sizing: border-box;
    transform: translate(-50%, -50%);
    animation: ringOrbit 22s linear infinite;
    box-shadow: 0 0 10px rgba(255, 200, 0, .28),
        inset 0 0 8px rgba(255, 200, 0, .08);
    will-change: transform;
}

.hero .ring::after {
    content: "";
    position: absolute;
    top: -5px;
    left: 50%;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #fff1a8;
    box-shadow: 0 0 8px 3px rgba(255, 212, 0, .85),
        0 0 20px 6px rgba(255, 170, 0, .45);
    transform: translateX(-50%);
}

.hero .ring.r2 {
    width: 96%;
    opacity: .35;
    border-width: 1px;
    border-top-color: rgba(255, 255, 255, .9);
    border-left-color: rgba(255, 190, 0, .7);
    animation: ringOrbit 34s linear infinite reverse;
}

.hero .ring.r2::after {
    top: -3px;
    width: 6px;
    height: 6px;
    background: #fff;
    box-shadow: 0 0 7px 2px rgba(255, 220, 100, .75),
        0 0 16px 4px rgba(255, 170, 0, .35);
}

.hero .halo {
    position: absolute;
    width: 70%;
    aspect-ratio: 1;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255, 200, 0, .28), transparent 68%);
    filter: blur(20px);
    animation: haloPulse 5s ease-in-out infinite alternate;
}

.tilt img {
    filter: drop-shadow(0 30px 40px rgba(255, 150, 0, .25))
        drop-shadow(0 0 60px rgba(255, 180, 0, .15));
}

@keyframes heroGlowDrift {
    to { transform: translate3d(26px, 18px, 0) scale(1.12); }
}
@keyframes heroSpotlightPulse {
    0%, 100% { opacity: .85; }
    50% { opacity: 1; }
}
@keyframes scanMove {
    0% { left: -20%; opacity: 0; }
    10% { opacity: 1; }
    60% { left: 100%; opacity: 1; }
    100% { left: 100%; opacity: 0; }
}
@keyframes ringOrbit {
    from { transform: translate(-50%, -50%) rotate(0deg); }
    to { transform: translate(-50%, -50%) rotate(360deg); }
}
@keyframes haloPulse {
    to { opacity: .62; transform: scale(1.12); }
}
"""

HERO_NETWORK_SCRIPT = """
/* Animated network points scoped to the transformer hero. */
(() => {
    const canvas = document.querySelector(".hero .bg-network");
    const hero = document.querySelector(".hero");
    if (!canvas || !hero || typeof canvas.getContext !== "function") return;

    const context = canvas.getContext("2d");
    if (!context) return;

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const mobileViewport = window.matchMedia("(max-width: 767px)");
    let width = 0;
    let height = 0;
    let points = [];
    let frame = 0;
    let linkDistance = 160;

    function draw(time) {
        const now = typeof time === "number" ? time : performance.now();
        context.clearRect(0, 0, width, height);

        for (let i = 0; i < points.length; i++) {
            const point = points[i];
            if (!reducedMotion.matches && !document.hidden) {
                point.x += point.vx;
                point.y += point.vy;
                if (point.x < 0 || point.x > width) point.vx *= -1;
                if (point.y < 0 || point.y > height) point.vy *= -1;
            }

            for (let j = i + 1; j < points.length; j++) {
                const other = points[j];
                const dx = point.x - other.x;
                const dy = point.y - other.y;
                const distance = Math.hypot(dx, dy);
                if (distance < linkDistance) {
                    const alpha = (1 - distance / linkDistance) * .4;
                    context.beginPath();
                    context.strokeStyle = `rgba(255, 200, 0, ${alpha})`;
                    context.lineWidth = .8;
                    context.moveTo(point.x, point.y);
                    context.lineTo(other.x, other.y);
                    context.stroke();
                }
            }

            const twinkle = .6 + .4 * Math.sin(now / 900 + point.phase);
            context.beginPath();
            context.fillStyle = `rgba(255, 210, 60, ${.55 * twinkle + .25})`;
            context.shadowColor = "rgba(255, 190, 0, .9)";
            context.shadowBlur = 8;
            context.arc(point.x, point.y, point.radius, 0, Math.PI * 2);
            context.fill();
        }

        context.shadowBlur = 0;
        if (!reducedMotion.matches && !document.hidden) {
            frame = window.requestAnimationFrame(draw);
        } else {
            frame = 0;
        }
    }

    function resize() {
        if (frame) {
            window.cancelAnimationFrame(frame);
            frame = 0;
        }

        const bounds = hero.getBoundingClientRect();
        const ratio = Math.min(window.devicePixelRatio || 1, 2);
        width = Math.max(1, bounds.width);
        height = Math.max(1, bounds.height);
        canvas.width = Math.round(width * ratio);
        canvas.height = Math.round(height * ratio);
        context.setTransform(ratio, 0, 0, ratio, 0, 0);

        const isMobile = mobileViewport.matches;
        const count = isMobile ? 35 : 70;
        linkDistance = isMobile ? 120 : 160;
        points = Array.from({ length: count }, () => ({
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - .5) * .25,
            vy: (Math.random() - .5) * .25,
            radius: Math.random() * 1.4 + .8,
            phase: Math.random() * Math.PI * 2,
        }));
        draw();
    }

    function updateMotion() {
        if (frame) {
            window.cancelAnimationFrame(frame);
            frame = 0;
        }
        draw();
    }

    if ("ResizeObserver" in window) {
        new ResizeObserver(resize).observe(hero);
    } else {
        window.addEventListener("resize", resize, { passive: true });
    }

    if (typeof mobileViewport.addEventListener === "function") {
        mobileViewport.addEventListener("change", resize);
    } else if (typeof mobileViewport.addListener === "function") {
        mobileViewport.addListener(resize);
    }

    if (typeof reducedMotion.addEventListener === "function") {
        reducedMotion.addEventListener("change", updateMotion);
    } else if (typeof reducedMotion.addListener === "function") {
        reducedMotion.addListener(updateMotion);
    }
    document.addEventListener("visibilitychange", updateMotion);
    resize();
})();
"""
