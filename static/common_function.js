console.log("✅ common_function.js 로드 완료");

$(document).ready(function () {
    const canvas = document.getElementById("psaCanvas");
    const magnifier = document.getElementById("magnifierCanvas");

    if (!canvas || !magnifier) {
        console.error("🚨 canvas 또는 magnifierCanvas 요소를 찾을 수 없습니다!");
        return;
    }

    const ctx = canvas.getContext("2d");
    const mCtx = magnifier.getContext("2d");

    const zoom = 1.2;
    const size = 100;
    let lastX = 0, lastY = 0;
    let img = null;  // 원본 이미지 객체

    // 이미지 로드 후 설정
    const imageSrc = localStorage.getItem("psaImage");
    if (!imageSrc) {
        console.error("🚨 localStorage에서 이미지 못 찾음");
        return;
    }

    img = new Image();
    img.onload = () => {
        const winWidth = window.innerWidth;
        const winHeight = window.innerHeight;

        const scale = Math.min(winWidth / img.naturalWidth, winHeight / img.naturalHeight);
        canvas.width = img.naturalWidth * scale;
        canvas.height = img.naturalHeight * scale;

        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    };
    img.src = imageSrc;

    canvas.addEventListener("mousemove", function (event) {
        const rect = canvas.getBoundingClientRect();
    
        // 마우스 좌표를 캔버스 기준으로 변환
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        const x = (event.clientX - rect.left) * scaleX;
        const y = (event.clientY - rect.top) * scaleY;
    
        lastX = x;
        lastY = y;
    
        // 확대경 위치 - 브라우저 상 마우스 위치 기준
        magnifier.style.display = "block";
        magnifier.style.left = `${event.pageX - size / 2}px`;
        magnifier.style.top = `${event.pageY - size / 2}px`;

    
        // 확대 대상 계산 - canvas 좌표 기준으로 확대
        const sw = size / zoom;
        const sh = size / zoom;
        const srcX = x - sw / 2;
        const srcY = y - sh / 2;
    
        mCtx.clearRect(0, 0, size, size);
        mCtx.save();
        mCtx.beginPath();
        mCtx.arc(size / 2, size / 2, size / 2, 0, Math.PI * 2);
        mCtx.clip();
    
        mCtx.drawImage(
            canvas,   // ⛳ 확대 대상은 원본 이미지가 아니라 현재의 캔버스
            srcX, srcY,
            sw, sh,
            0, 0,
            size, size
        );
    
        drawCrosshair(mCtx, size);
        mCtx.restore();
    });
    
    canvas.addEventListener("mouseleave", function () {
        magnifier.style.display = "none";
    });

    canvas.addEventListener("click", function () {
        ctx.fillStyle = "red";
        ctx.beginPath();
        ctx.arc(lastX, lastY, 2, 0, Math.PI * 2);
        ctx.fill();

        console.log("📍 클릭 위치:", lastX.toFixed(2), lastY.toFixed(2));
    });

    function drawCrosshair(ctx, size) {
        const center = size / 2;
        const length = 6;

        ctx.strokeStyle = "black";
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(center - length, center);
        ctx.lineTo(center + length, center);
        ctx.moveTo(center, center - length);
        ctx.lineTo(center, center + length);
        ctx.stroke();
    }
});
