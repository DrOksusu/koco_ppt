// ✅ 음성 출력 함수
window.speakMessage = function(message) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(message);
        utterance.lang = 'ko-KR'; 
        utterance.rate = 2; 
        utterance.pitch = 1.0; 
        utterance.volume = 1.0; 
        window.speechSynthesis.speak(utterance);
    } else {
        console.warn("🚨 현재 브라우저는 음성 출력을 지원하지 않습니다.");
    }
}

// ✅ dataURL을 Blob으로 변환하는 함수 추가
window.dataURLtoBlob = function () {
    let arr = dataURL.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new Blob([u8arr], { type: mime });
}


// ✅ 초록색 직선 그리는 함수
window.drawGreenLine = function(points, scaleX, scaleY, ctx) {
    if (points.length < 2) return;

    const p1 = [points[0][0] * scaleX, points[0][1] * scaleY];
    const p2 = [points[1][0] * scaleX, points[1][1] * scaleY];

    ctx.strokeStyle = "green";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(p1[0], p1[1]);
    ctx.lineTo(p2[0], p2[1]);
    ctx.stroke();
}

// ✅ 빨간색 직선 그리는 함수
window.drawRedLine = function(points, scaleX, scaleY, ctx) {
    if (points.length < 3) return;

    const p1 = [points[0][0] * scaleX, points[0][1] * scaleY];
    const p3 = [points[2][0] * scaleX, points[2][1] * scaleY];

    const dx = p3[0] - p1[0];
    const dy = p3[1] - p1[1];

    const extendedP3 = [p3[0] + dx * 3, p3[1] + dy * 3];

    ctx.strokeStyle = "red";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(p1[0], p1[1]);
    ctx.lineTo(extendedP3[0], extendedP3[1]);
    ctx.stroke();
}

// ✅ 파란색 직선 그리는 함수
window.drawBlueLine = function(points, scaleX, scaleY, ctx) {
    if (points.length < 4) return;

    const p1 = [points[0][0] * scaleX, points[0][1] * scaleY];
    const p3 = [points[2][0] * scaleX, points[2][1] * scaleY];
    const p4 = [points[3][0] * scaleX, points[3][1] * scaleY];

    const dx = p3[0] - p1[0];
    const dy = p3[1] - p1[1];

    let p_perp;
    if (dx === 0) {
        p_perp = [p1[0], p4[1]];
    } else if (dy === 0) {
        p_perp = [p4[0], p1[1]];
    } else {
        const m = dy / dx;
        const m_perp = -1 / m;
        const b = p1[1] - m * p1[0];
        const b_perp = p4[1] - m_perp * p4[0];
        const x_perp = (b_perp - b) / (m - m_perp);
        const y_perp = m * x_perp + b;
        p_perp = [x_perp, y_perp];
    }

    ctx.strokeStyle = "blue";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(p4[0], p4[1]);
    ctx.lineTo(p_perp[0], p_perp[1]);
    ctx.stroke();
}

