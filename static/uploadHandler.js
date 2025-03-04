document.addEventListener("DOMContentLoaded", function () {
    /**
     * 특정 영역(Drop Zone)을 파일 업로드 기능과 연결하는 함수
     */
    function setupDropZone(dropZoneId, fileInputId) {
        const dropZone = document.getElementById(dropZoneId);
        const fileInput = document.getElementById(fileInputId);

        if (!dropZone || !fileInput) return;

        dropZone.addEventListener("click", () => fileInput.click());
        fileInput.addEventListener("change", () => handleFilePreview(fileInput, dropZone));

        dropZone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropZone.classList.add("drag-over");
        });

        dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));

        dropZone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropZone.classList.remove("drag-over");

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFilePreview(fileInput, dropZone);
            }
        });
    }

    /**
     * 파일을 선택한 후 미리보기를 생성하는 함수
     */
    function handleFilePreview(fileInput, dropZone) {
        const file = fileInput.files[0];

        if (file) {
            const reader = new FileReader();

            reader.onload = (e) => {
                dropZone.innerHTML = `<img src="${e.target.result}" alt="미리보기">
                                      <button class="delete-btn">X</button>`;

                dropZone.querySelector(".delete-btn").addEventListener("click", (event) => {
                    event.stopPropagation();
                    fileInput.value = "";
                    dropZone.innerHTML = "📂 파일 선택";
                });
            };

            reader.readAsDataURL(file);
        }
    }
    
    /**
     * PSA 선 그리기 버튼 이벤트 처리
     */
    document.getElementById("drawPSALine").addEventListener("click", (event) => {
        event.preventDefault();

        const fileInput = document.getElementById("lateral_ceph");

        if (!fileInput.files || fileInput.files.length === 0) {
            alert("⚠️ lateral_ceph에 업로드된 이미지가 없습니다!");
            return;
        }

        const file = fileInput.files[0];
        const reader = new FileReader();

        reader.onload = function (e) {
            const newWindow = window.open("", "_blank", "width=700,height=700,scrollbars=yes");
            newWindow.name = "firstWindow";

           // HTML 및 스타일 추가
           newWindow.document.write(`
            <html>
            <head>
                <title>확대된 Lateral Ceph</title>
                <style>
                    body { display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f0f0f0; }
                    #image-container { position: relative; display: inline-block; }
                    img { max-width: 90%; max-height: 90%; border: 2px solid black; cursor: crosshair; display: block; }
                    .marker {
                        position: absolute;
                        width: 3px;
                        height: 3px;
                        background-color: red;
                        border-radius: 50%;
                        transform: translate(-50%, -50%);
                        z-index: 9999;
                    }
                    /* ✅ 가이드 메시지 스타일 */
                    .guide-message {
                        position: absolute;
                        top: 20px;
                        left: 50%;
                        transform: translateX(-50%);
                        background: rgba(0, 0, 0, 0.7);
                        color: white;
                        padding: 10px 15px;
                        font-size: 16px;
                        border-radius: 5px;
                        z-index: 10000;
                    }
                </style>
            </head>
            <body>
                <div id="image-container">
                    <div id="guideMessage" class="guide-message">첫 번째 점을 찍으세요(lower incisor tip)</div> <!-- ✅ 초기 메시지 -->
                    <img src="${e.target.result}" id="expandedImage" alt="확대된 X-ray">
                </div>
                <script>
                    setTimeout(() => {
                        const points = [];
                        const img = document.getElementById("expandedImage");
                        const container = document.getElementById("image-container");
                        const guideMessage = document.getElementById("guideMessage");

                        // ✅ 단계별 가이드 메시지 리스트
                        const messages = [
                            "첫 번째 점(lower incisor)을 찍으세요",
                            "두 번째 점(hinge point)을 찍으세요",
                            "세 번째 점(하악6번 distobuccal cusp)을 찍으세요",
                            "네 번째 점(symphysis lingual 최대풍융부)을 찍으세요"
                        ];

                        img.addEventListener("click", function(event) {
                            if (points.length >= 4) {
                                guideMessage.style.display = "none"; // ✅ 4개 점이 찍히면 메시지 숨김
                                alert("✅ 4개의 좌표가 선택되었습니다.");
                                return;
                            }

                            const rect = img.getBoundingClientRect();
                            const originalWidth = img.naturalWidth;
                            const originalHeight = img.naturalHeight;
                            

                            const x = event.clientX - rect.left;
                            const y = event.clientY - rect.top;
                            

                            // 원본 크기에 맞춰 변환
                            const scaleX = originalWidth / rect.width;
                            const scaleY = originalHeight / rect.height;
                            const realX = Math.round(x * scaleX);
                            const realY = Math.round(y * scaleY);

                            points.push([realX, realY]);
                            console.log("📍 변환된 클릭 좌표:", realX, realY);

                            // 빨간 점 추가
                            const marker = document.createElement("div");
                            marker.classList.add("marker");
                            marker.style.left = x + "px";
                            marker.style.top = y + "px";
                            img.parentNode.appendChild(marker); // ✅ 이미지 위에 빨간 점 추가

                            // ✅ 다음 가이드 메시지 표시
                            if (points.length < 4) {
                                guideMessage.innerText = messages[points.length];
                            } else {
                                guideMessage.style.display = "none"; // ✅ 모든 점을 찍으면 메시지 숨김
                            }

                            if (points.length === 4) {
                                setTimeout(() => {
                                    alert("✅ 4개의 좌표가 선택되었습니다.");
                                    console.log("📌 최종 좌표 목록:", points);
                                    
                                   

                                    // ✅ 부모 창(Console)에서도 로그 확인 가능하도록 부모 함수 호출
                                    if (window.opener && !window.opener.closed && typeof window.opener.logFromChild === "function") {
                                        window.opener.logFromChild(points);
                                    } else {
                                        alert("🚨 부모 창이 없습니다. 좌표 데이터를 보낼 수 없습니다.");
                                    }
                                }, 100); // ✅ 빨간 점이 찍힌 후 0.1초 뒤에 실행
                            }
                        });
                    }, 500); // ✅ 실행 보장 (0.5초 딜레이)
                <\/script>S
            </body>
            </html>
        `);
    };

reader.readAsDataURL(file);
});
    /**
     * 로그 출력 함수 (디버깅용)
     */
    function logInfo(...args) {
        console.log("[INFO]", ...args);
    }

    function logError(...args) {
        console.error("[ERROR]", ...args);
    }

    /**
     * 폼 제출 시 데이터를 서버로 전송하는 함수
     */
    
    // Drop Zone 설정
    setupDropZone("xrayPreview1", "pano");
    setupDropZone("xrayPreview2", "lateral_ceph");
    setupDropZone("xrayPreview3", "frontal_ceph");
    setupDropZone("xrayPreview4", "psa");
    setupDropZone("excelPreview", "excel_data");

    for (let i = 1; i <= 8; i++) setupDropZone(`photoPreview${i}`, `photo${i}`);
    for (let i = 1; i <= 5; i++) setupDropZone(`oralPhotoPreview${i}`, `oralPhoto${i}`);
    for (let i = 1; i <= 8; i++) setupDropZone(`posturePhotoPreview${i}`, `posturePhoto${i}`);
});
