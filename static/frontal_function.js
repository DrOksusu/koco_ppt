// ✅ 두 점을 받아서 파란색 직선을 그리는 함수
window.drawBlueLineBetweenPoints = function (p1, p2, scaleX, scaleY, ctx) {
    // ⬇️ 입력된 점의 좌표에 스케일 적용
    const scaledP1 = [p1[0] * scaleX, p1[1] * scaleY];
    const scaledP2 = [p2[0] * scaleX, p2[1] * scaleY];
  
    // ⬇️ 캔버스에 파란색 직선 그리기
    ctx.strokeStyle = "blue";   // 선 색상 파란색
    ctx.lineWidth = 1;          // 선 두께
    ctx.beginPath();
    ctx.moveTo(scaledP1[0], scaledP1[1]); // 시작점 이동
    ctx.lineTo(scaledP2[0], scaledP2[1]); // 끝점까지 선 긋기
    ctx.stroke();
  };

  function getPerpendicularFoot(p3, p4, p9) {
    const [x3, y3] = p3;
    const [x4, y4] = p4;
    const [x9, y9] = p9;
  
    const dx = x4 - x3;
    const dy = y4 - y3;
  
    const dx9 = x9 - x3;
    const dy9 = y9 - y3;
  
    const dot = dx * dx9 + dy * dy9;
    const lenSq = dx * dx + dy * dy;
    const t = dot / lenSq;
  
    const x_perp = x3 + t * dx;
    const y_perp = y3 + t * dy;
  
    return [x_perp, y_perp];
  }

  function drawPerpendicularDashedLine(p3, p4, p9, scaleX, scaleY, ctx) {
    // 수직 투영된 점 계산
    const [x_perp, y_perp] = getPerpendicularFoot(p3, p4, p9);
  
    // 캔버스 스케일 적용
    const xPerpCanvas = x_perp * scaleX;
    const yPerpCanvas = y_perp * scaleY;
    const x9Canvas = p9[0] * scaleX;
    const y9Canvas = p9[1] * scaleY;
  
    // ✅ p9까지 벡터
    const dx = x9Canvas - xPerpCanvas;
    const dy = y9Canvas - yPerpCanvas;
  
    // ✅ 반대 방향 4배 연장
    const extendedX = xPerpCanvas - dx * 2.7;
    const extendedY = yPerpCanvas - dy * 2.7;
  
    // 빨간 점선 스타일
    ctx.strokeStyle = "yellow";
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]); // 점선
  
    ctx.beginPath();
    ctx.moveTo(xPerpCanvas, yPerpCanvas);
    ctx.lineTo(x9Canvas, y9Canvas); // 수직 투사점 → p9
    ctx.stroke();
  
    ctx.beginPath();
    ctx.moveTo(xPerpCanvas, yPerpCanvas);
    ctx.lineTo(extendedX, extendedY); // 수직 투사점 → 반대 방향
    ctx.stroke();
  
    ctx.setLineDash([]); // 점선 초기화
  }

  function drawExtendedGreenLine(p3, p4, p10, scaleX, scaleY, ctx) {
    // 1️⃣ 수직 투영된 점 계산
    const [x_perp, y_perp] = getPerpendicularFoot(p3, p4, p10);
  
    // 2️⃣ 캔버스 스케일 적용
    const xPerpCanvas = x_perp * scaleX;
    const yPerpCanvas = y_perp * scaleY;
    const x9Canvas = p10[0] * scaleX;
    const y9Canvas = p10[1] * scaleY;
  
    // 3️⃣ p9까지 벡터 계산
    const dx = x9Canvas - xPerpCanvas;
    const dy = y9Canvas - yPerpCanvas;
  
    // 4️⃣ 반대 방향으로 2배 연장
    const reverseX = xPerpCanvas - dx * 2.5;
    const reverseY = yPerpCanvas - dy * 2.5;
  
    // 5️⃣ 동측 방향으로 4배 연장
    const forwardX = xPerpCanvas + dx * 4.5;
    const forwardY = yPerpCanvas + dy * 4.5;
  
    // 6️⃣ 초록색 점선 스타일 설정
    ctx.strokeStyle = "green";
    ctx.lineWidth = 1;
    ctx.setLineDash([5,5]); // 점선
  
    // 7️⃣ 선 그리기
    ctx.beginPath();
    ctx.moveTo(reverseX, reverseY); // 반대 방향 끝점
    ctx.lineTo(forwardX, forwardY); // p9 방향 끝점
    ctx.stroke();

    // 8️⃣ 점선 초기화
    ctx.setLineDash([]); // 점선 초기화
  }

  function drawRedDashedLineP12toP11(p3, p4, p10, p11, scaleX, scaleY, ctx) {
    // 1️⃣ p12 계산 (p3, p4에 대한 p10의 수직 발)
    const [x12, y12] = getPerpendicularFoot(p3, p4, p10);
  
    // 2️⃣ p11은 입력으로 받아옴
    const x11 = p11[0];
    const y11 = p11[1];
  
    // 3️⃣ 캔버스 스케일 적용
    const x12Canvas = x12 * scaleX;
    const y12Canvas = y12 * scaleY;
    const x11Canvas = x11 * scaleX;
    const y11Canvas = y11 * scaleY;
  
    // 4️⃣ 빨간 점선 스타일
    ctx.strokeStyle = "red";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([5, 5]); // 점선
  
    // 5️⃣ 선 그리기
    ctx.beginPath();
    ctx.moveTo(x12Canvas, y12Canvas);
    ctx.lineTo(x11Canvas, y11Canvas);
    ctx.stroke();
  
    ctx.setLineDash([]); // 점선 초기화
  }
  
  function calculateAngleBetweenLines(p3, p4, p10, p11) {
    // 1️⃣ 초록색 선의 방향 벡터 (p3-p4에 수직이고 p10을 지나는 직선)
    const [x12, y12] = getPerpendicularFoot(p3, p4, p10);
  
    // 초록색 선 벡터 (p12 → p10)
    const green_dx = p10[0] - x12;
    const green_dy = p10[1] - y12;
  
    // 빨간색 선 벡터 (p12 → p11)
    const red_dx = p11[0] - x12;
    const red_dy = p11[1] - y12;
  
    // 2️⃣ 벡터 내적
    const dotProduct = green_dx * red_dx + green_dy * red_dy;
  
    // 3️⃣ 벡터 길이 (norm)
    const greenLength = Math.sqrt(green_dx * green_dx + green_dy * green_dy);
    const redLength = Math.sqrt(red_dx * red_dx + red_dy * red_dy);
  
    // 4️⃣ 코사인 값
    const cosTheta = dotProduct / (greenLength * redLength);
  
    // 5️⃣ 각도 (라디안 → 디그리 변환)
    const angleRad = Math.acos(cosTheta);
    const angleDeg = angleRad * (180 / Math.PI);
  
    return angleDeg.toFixed(2); // 소수점 둘째자리까지 반환
  }
  
  function drawAngleAtBottom(ctx, canvas, angle) {
    const angleText = `ZA - Menton angle: ${angle}°`;
  
    ctx.font = "bold 24px sans-serif"; // 글자 폰트
    ctx.fillStyle = "red";             // 글자 색
    ctx.textAlign = "center";            // 가로 중앙
    ctx.textBaseline = "bottom";         // 세로 하단
  
    ctx.fillText(angleText, canvas.width / 2, canvas.height - 10); // (x, y)
  }
  

  
    
  
  