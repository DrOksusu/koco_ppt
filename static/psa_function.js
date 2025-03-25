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

function showGaugeCanvas() {
    const gaugeCanvas = document.getElementById("gaugeCanvas");
    gaugeCanvas.style.display = "block";  // ✅ 캔버스 보이도록 변경
}

// ✅ P1과 P_perp의 거리 D1을 구하는 함수
function calculateDistance(p1, p2) {
    return Math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2).toFixed(2);
}

// ✅ 검은색 직선 그리는 함수 (첫 번째와 두 번째 점 연결, 첫 점 방향으로 연장)
window.drawBlackLine = function(points, scaleX, scaleY, ctx) {
    if (points.length < 2) return;

    const p1 = [points[0][0] * scaleX, points[0][1] * scaleY];
    const p2 = [points[1][0] * scaleX, points[1][1] * scaleY];

    // ✅ 방향 벡터 계산
    const dx = p2[0] - p1[0];
    const dy = p2[1] - p1[1];

    // ✅ 첫 번째 점 방향으로 50% 연장된 지점 계산
    const extendedP1 = [p1[0] - dx * 0.5, p1[1] - dy * 0.5];

    ctx.strokeStyle = "black";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(extendedP1[0], extendedP1[1]); // 연장된 지점에서 시작
    ctx.lineTo(p2[0], p2[1]); // 두 번째 점까지 선 긋기
    ctx.stroke();
}

window.drawBlackDashedLine = function (points, scaleX, scaleY, ctx) {
    if (points.length < 2) return;

    const p1 = [points[0][0] * scaleX, points[0][1] * scaleY];
    const p2 = [points[1][0] * scaleX, points[1][1] * scaleY];

    const dx = p1[0] - p2[0];
    const dy = p1[1] - p2[1];
    const length = Math.sqrt(dx * dx + dy * dy);

    const ux = dx / length;
    const uy = dy / length;

    // ✅ 6.5도 반시계 방향 회전
    const angle = (6.5 * Math.PI) / 180;
    const cos = Math.cos(angle);
    const sin = Math.sin(angle);

    const rx = ux * cos - uy * sin;
    const ry = ux * sin + uy * cos;

    // ✅ 회전된 벡터를 기준 벡터에 대해 대칭시키기 (데칼코마니 효과)
    const dot = rx * ux + ry * uy;
    const reflectedX = 2 * dot * ux - rx;
    const reflectedY = 2 * dot * uy - ry;

    const lineLength = length * 1.1;
    const endX = p2[0] + reflectedX * lineLength;
    const endY = p2[1] + reflectedY * lineLength;

    // ✅ 점선 그리기
    ctx.save();
    ctx.strokeStyle = "black";
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);

    ctx.beginPath();
    ctx.moveTo(p2[0], p2[1]); // 기준 실선 끝점에서 시작
    ctx.lineTo(endX, endY);   // 데칼코마니 방향으로
    ctx.stroke();

    ctx.restore();
};


// ✅ 초록색 직선 그리는 함수
window.drawGreenLine = function(points, scaleX, scaleY, ctx) {
    if (points.length < 2) return;

    const p1 = [points[2][0] * scaleX, points[2][1] * scaleY];
    const p2 = [points[3][0] * scaleX, points[3][1] * scaleY];

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

    const p1 = [points[3][0] * scaleX, points[3][1] * scaleY];
    const p3 = [points[4][0] * scaleX, points[4][1] * scaleY];

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

    const p1 = [points[3][0] * scaleX, points[3][1] * scaleY]; // 네 번째 점 lower incisor tip
    const p3 = [points[4][0] * scaleX, points[4][1] * scaleY]; // 다섯번째 점 occlusal point
    const p4 = [points[5][0] * scaleX, points[5][1] * scaleY]; // 네 번째 점 (수선을 내릴 점)

    const dx = p3[0] - p1[0];
    const dy = p3[1] - p1[1];

    console.log("📌 원래 직선 기울기 계산: dx =", dx, ", dy =", dy);

    let p_perp; // 수직 교점 좌표

    if (dx === 0) {
        console.warn("⚠️ 수직선이므로 수선의 발을 단순 계산합니다.");
        p_perp = [p1[0], p4[1]];
    } else if (dy === 0) {
        console.warn("⚠️ 수평선이므로 수선의 발을 단순 계산합니다.");
        p_perp = [p4[0], p1[1]];
    } else {
        const m = dy / dx; // 원래 선의 기울기

        if (m === 0) {
            console.error("🚨 기울기(m)가 0이므로 계산을 중단합니다.");
            return;
        }

        const m_perp = -1 / m; // 수선의 기울기 (음의 역수)
        const b = p1[1] - m * p1[0]; // 원래 직선의 y절편
        const b_perp = p4[1] - m_perp * p4[0]; // 수선의 y절편

        console.log("📌 수선과 원래 직선의 방정식: y =", m, "x +", b, " | y =", m_perp, "x +", b_perp);

        const denominator = m - m_perp; // 분모 계산

        if (denominator === 0) {
            console.error("🚨 분모가 0이므로 수선의 발 계산 불가능.");
            return;
        }

        const x_perp = (b_perp - b) / denominator;
        const y_perp = m * x_perp + b;

        p_perp = [parseFloat(x_perp.toFixed(2)), parseFloat(y_perp.toFixed(2))]; // 소수점 2자리로 제한
        // ✅ 수선의 발을 계산한 후, `scaleX`, `scaleY`를 곱해서 변환
        
        }

    console.log("📌 수선의 발 좌표 (스케일 조정전):", p_perp);

    // ✅ 파란색 선 그리기 (p4에서 p_perp까지)
    ctx.strokeStyle = "blue";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(p4[0], p4[1]);
    ctx.lineTo(p_perp[0], p_perp[1]);
    ctx.stroke();

    // ✅ P_perp을 다시 스케일 적용해서 P1과 같은 좌표계로 변환
    const p_perp_scaled = [p_perp[0] / scaleX, p_perp[1] / scaleY];
    console.log("📌 수선의 발 좌표 (스케일 조정후):", p_perp_scaled);
    console.log("points[0]:", points[0]);

     // ✅ P1과 P_perp (같은 좌표계) 사이의 거리 D1 계산
     const D1 = calculateDistance(points[3], p_perp_scaled);
     console.log("📏 D1 (P1 - P_perp 거리):", D1);

    // ✅ P_perp (원래 좌표계로 변환된 값 반환)
    return { p_perp:p_perp_scaled, D1 };
};


function drawYellowCircles(ctx, points, scaleX, scaleY, p_perp) {
    if (points.length < 6) {
        console.error("❌ 최소 4개의 좌표가 필요합니다.");
        return { intersection: null, D2: 0 };
    }

    console.log("📍 points:", points);

    let p1_x = points[3][0], p1_y = points[3][1];
    let a = points[2][0], b = points[2][1]; // hinge point
    let c = points[3][0], d = points[3][1]; // lower incisor tip

    let x0 = Math.round((a + c) / 2 - (Math.sqrt(3) * (d - b)) / 2);
    let y0 = Math.round((b + d) / 2 + (Math.sqrt(3) * (c - a)) / 2);

    let x1 = Math.round((a + c) / 2 + (Math.sqrt(3) * (d - b)) / 2);
    let y1 = Math.round((b + d) / 2 - (Math.sqrt(3) * (c - a)) / 2);

    let x = x0 > x1 ? x0 : x1;
    let y = y0 < y1 ? y0 : y1;

    let radius = Math.round(Math.sqrt((a - c) ** 2 + (b - d) ** 2));
    console.log(`🟡 첫 번째 원 중심: (${x}, ${y}), 반지름: ${radius}`);

    ctx.strokeStyle = "yellow";
    ctx.lineWidth = 1;

    ctx.beginPath();
    ctx.arc(x * scaleX, y * scaleY, radius * scaleX, 0, Math.PI * 2);
    ctx.stroke();

    let x1_red = points[3][0], y1_red = points[3][1];
    let x2_red = points[4][0], y2_red = points[4][1];

    let dx = x2_red - x1_red;
    let dy = y2_red - y1_red;

    if (dx === 0) {
        let x_intersect = x1_red;
        let delta = Math.sqrt(radius ** 2 - (x_intersect - x) ** 2);
        return [[x_intersect, y + delta], [x_intersect, y - delta]].filter(p => !(p[0] === p1_x && p[1] === p1_y));
    }

    let m_red = dy / dx;
    let b_red = y1_red - m_red * x1_red;

    let A = 1 + m_red ** 2;
    let B = 2 * (m_red * (b_red - y) - x);
    let C = x ** 2 + (b_red - y) ** 2 - radius ** 2;

    let D = B ** 2 - 4 * A * C;

    if (D < 0) {
        console.warn("⚠️ 교점이 없습니다 (빨간색 선과 노란색 원이 만나지 않음)");
        return { intersection: null, D2: 0 };
    }

    let x_intersect1 = (-B + Math.sqrt(D)) / (2 * A);
    let x_intersect2 = (-B - Math.sqrt(D)) / (2 * A);

    let y_intersect1 = m_red * x_intersect1 + b_red;
    let y_intersect2 = m_red * x_intersect2 + b_red;

    let intersections = [[x_intersect1, y_intersect1], [x_intersect2, y_intersect2]];
    console.log("🟡 빨간색 선과 노란색 원의 교차점:", intersections)

    // ✅ 첫 번째 점(P1)과 거의 같은 좌표를 제거 (미세한 오차 고려)
    intersections = intersections.filter(p => !(
        Math.abs(p[0] - p1_x) <= Math.abs(p1_x * 0.02) &&  // X 좌표 0.1% 오차 범위
        Math.abs(p[1] - p1_y) <= Math.abs(p1_y * 0.02)     // Y 좌표 0.1% 오차 범위
    ));

    if (intersections.length === 0) {
        console.warn("⚠️ 첫 번째 점과 동일한 교점 제거 후 남은 교점이 없음.");
        return { intersection: null, D2: 0 };
    }

    let intersection = intersections[0];   
    console.log("🟡 빨간색 선과 노란색 원의 교차점:", intersection);

    if (!p_perp || !intersection) {
        console.error("🚨 p_perp 또는 intersection 값이 유효하지 않음.");
        return { intersection: null, D2: 0 };
    }

    let D2 = calculateDistance([p_perp[0], p_perp[1]], intersection);

    // ✅ 중심 좌표 (스케일 적용된 값)도 함께 반환
    const circleCenter = [x , y];
    console.log("📏 D2 (P_perp - 교점 거리):", D2, circleCenter);
    console.log("circleCenter:", circleCenter);
    console.log("scaleX:", scaleX);
    console.log("scaleY:", scaleY);


    return { intersection, D2, circleCenter };
    
}


function drawArrowFromYellowCircle(
    HGI = 0,
    VGI = 0,
    ctx,
    x, y,              // 중심 좌표 (원본 좌표계)
    scaleX, scaleY     // 스케일
) {
    if (isNaN(HGI) || isNaN(VGI)) {
        console.warn("❌ HGI 또는 VGI 값이 숫자가 아닙니다. 기본값(0)으로 처리합니다.");
        HGI = 0;
        VGI = 0;
    }

    const startX = x * scaleX;
    const startY = y * scaleY;

    const endX = startX + HGI*20 * scaleX;
    const endY = startY - VGI*20 * scaleY;

    console.log(`🎯 화살표 시작: (${startX}, ${startY}) → (${endX}, ${endY})`);

    ctx.strokeStyle = "red";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(endX, endY);
    ctx.stroke();

    const dx = endX - startX;
    const dy = endY - startY;
    const len = Math.sqrt(dx * dx + dy * dy);

    if (len === 0) {
        console.warn("⚠️ HGI, VGI가 0이므로 화살 길이 없음");
        return;
    }

    const unitX = dx / len;
    const unitY = dy / len;
    const arrowSize = 10;

    const leftX = endX - arrowSize * (unitX + unitY);
    const leftY = endY - arrowSize * (unitY - unitX);
    const rightX = endX - arrowSize * (unitX - unitY);
    const rightY = endY - arrowSize * (unitY + unitX);

    ctx.beginPath();
    ctx.moveTo(endX, endY);
    ctx.lineTo(leftX, leftY);
    ctx.lineTo(rightX, rightY);
    ctx.closePath();
    ctx.fillStyle = "red";
    ctx.fill();

    console.log("✅ 화살표 그리기 완료 (노란 원 중심 기준)");
};



// ✅ 게이지 스타일 설정
const GAUGE_COLORS = {
    safe: "green",   // 50 ~ 150
    warning: "yellow",  // 0 ~ 50
    danger: "red"  // 150 이상
};

// ✅ 게이지를 그리는 함수
function drawGauge(ctx, value, maxValue, x, y, radius, label) {
    // ✅ value가 숫자가 아니면 기본값 0으로 설정
    if (value === undefined || value === null || isNaN(value)) {
        console.error(`🚨 ${label} 값이 올바르지 않습니다:`, value);
        value = 0; // 기본값 설정
    } else {
        // ✅ 문자열로 들어온 경우 숫자로 변환
        value = Number(value);
    }

    ctx.clearRect(x - radius - 10, y - radius - 10, (radius + 10) * 2, (radius + 10) * 2);
    
    // ✅ 게이지 색상 결정
    let color;
    if (value <= 50) color = GAUGE_COLORS.warning;
    else if (value <= 150) color = GAUGE_COLORS.safe;
    else color = GAUGE_COLORS.danger;

    // ✅ 원형 게이지 바탕
    ctx.beginPath();
    ctx.arc(x, y, radius, 0.75 * Math.PI, 2.25 * Math.PI);
    ctx.strokeStyle = "#ccc"; // 배경
    ctx.lineWidth = 10;
    ctx.stroke();

    // ✅ 현재 값에 따른 게이지 채우기
    const endAngle = 0.75 * Math.PI + (value / maxValue) * (1.5 * Math.PI);
    ctx.beginPath();
    ctx.arc(x, y, radius, 0.75 * Math.PI, endAngle);
    ctx.strokeStyle = color;
    ctx.lineWidth = 10;
    ctx.stroke();

    // ✅ 중앙 텍스트 값 표시
    ctx.fillStyle = "#000";
    ctx.font = "16px Arial";
    ctx.textAlign = "center";
    ctx.fillText(label, x, y - 15);
    ctx.fillText(`${value.toFixed(1)}`, x, y + 10);
}

// ✅ HTML 캔버스에 게이지를 그리는 함수
function updateDashboard(guideDistance, bufferDistance) {
    const canvas = document.getElementById("gaugeCanvas");

    if (!canvas) {
        console.error("🚨 오류: gaugeCanvas 요소를 찾을 수 없습니다!");
        return;
    }

    const ctx = canvas.getContext("2d");

    if (!ctx) {
        console.error("🚨 오류: 2D 컨텍스트를 가져올 수 없습니다!");
        return;
    }
   
    const maxValue = 100;

    drawGauge(ctx, guideDistance, maxValue, 100, 50, 25, "Guide Zone");
    drawGauge(ctx, bufferDistance, maxValue, 250, 50, 25, "Buffer Zone");
}

// ✅ 자동차 계기판 UI를 업데이트하는 함수
function updateCarDashboard(blue_result, yellow_result) {
    if (!blue_result || !yellow_result) {
        console.error("🚨 Guide Zone 또는 Buffer Zone 값을 가져오지 못했습니다.");
        return;
    }

    console.log("🚗 계기판 업데이트!");
    console.log("🔵 Guide Zone:", blue_result.D1);
    console.log("🟡 Buffer Zone:", yellow_result.D2);

    updateDashboard(blue_result.D1, yellow_result.D2);
}

