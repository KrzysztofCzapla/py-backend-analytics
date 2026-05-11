function drawChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;

    // Set display size
    const width = canvas.parentElement.clientWidth - 40;
    const height = 250;

    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    if (!data || data.length === 0) {
        ctx.fillStyle = "#9ca3af";
        ctx.textAlign = "center";
        ctx.fillText("No data recorded yet", width / 2, height / 2);
        return;
    }

    const padding = { top: 30, right: 20, bottom: 40, left: 45 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    const values = data.map(d => Number(d.count || 0));
    const maxVal = Math.max(...values, 5);
    const gridSteps = 4;

    // 1. Draw Grid System
    ctx.strokeStyle = "#f3f4f6";
    ctx.lineWidth = 1;
    ctx.textAlign = "right";
    ctx.fillStyle = "#9ca3af";
    ctx.font = "10px Inter, sans-serif";

    for (let i = 0; i <= gridSteps; i++) {
        const y = padding.top + (chartHeight / gridSteps) * i;
        const label = Math.round(maxVal - (maxVal / gridSteps) * i);

        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(width - padding.right, y);
        ctx.stroke();
        ctx.fillText(label, padding.left - 10, y + 3);
    }

    // 2. Draw Data
    const barGap = 0.3; // 30% gap
    const step = chartWidth / data.length;
    const barWidth = step * (1 - barGap);

    data.forEach((d, i) => {
        const val = Number(d.count || 0);
        const barHeight = (val / maxVal) * chartHeight;
        const x = padding.left + (i * step) + (step * barGap / 2);
        const y = height - padding.bottom - barHeight;

        // Gradient for bars
        const gradient = ctx.createLinearGradient(0, y, 0, height - padding.bottom);
        gradient.addColorStop(0, "#3b82f6");
        gradient.addColorStop(1, "#60a5fa");

        ctx.fillStyle = gradient;

        // Render rounded bar
        if (barHeight > 0) {
            const r = Math.min(barWidth / 2, 6);
            ctx.beginPath();
            ctx.moveTo(x, y + r);
            ctx.quadraticCurveTo(x, y, x + r, y);
            ctx.lineTo(x + barWidth - r, y);
            ctx.quadraticCurveTo(x + barWidth, y, x + barWidth, y + r);
            ctx.lineTo(x + barWidth, height - padding.bottom);
            ctx.lineTo(x, height - padding.bottom);
            ctx.closePath();
            ctx.fill();
        }

        // X-Axis Labels (Conditional spacing)
        const showEvery = Math.ceil(data.length / 8);
        if (i % showEvery === 0 || i === data.length - 1) {
            ctx.save();
            ctx.translate(x + barWidth / 2, height - padding.bottom + 15);
            ctx.rotate(Math.PI / 8);
            ctx.textAlign = "left";
            ctx.fillStyle = "#6b7280";
            ctx.fillText(d.date || d.day || i, 0, 0);
            ctx.restore();
        }
    });
}
