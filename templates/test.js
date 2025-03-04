<script>
    function setupDropZone(dropZoneId, fileInputId) {
      const dropZone = document.getElementById(dropZoneId);
      const fileInput = document.getElementById(fileInputId);

      // Drop Zone 클릭 시 파일 선택 창 열기
      dropZone.addEventListener("click", function () {
        fileInput.click();
      });

      // 파일 선택 시 미리보기 표시
      fileInput.addEventListener("change", function () {
        handleFilePreview(fileInput, dropZone);
      });

      // 드래그 앤 드롭 이벤트 처리
      dropZone.addEventListener("dragover", function (e) {
        e.preventDefault();
        dropZone.classList.add("drag-over");
      });

      dropZone.addEventListener("dragleave", function () {
        dropZone.classList.remove("drag-over");
      });

      dropZone.addEventListener("drop", function (e) {
        e.preventDefault();
        dropZone.classList.remove("drag-over");

        const files = e.dataTransfer.files;
        if (files.length > 0) {
          fileInput.files = files;
          handleFilePreview(fileInput, dropZone);
        }
      });
    }

    function handleFilePreview(fileInput, dropZone) {
      const file = fileInput.files[0];
      if (file) {
          const reader = new FileReader();

          reader.onload = function (e) {
              // ✅ 파일 박스에 미리보기 이미지 추가
              dropZone.innerHTML = `<img src="${e.target.result}" alt="미리보기">
                                    <button class="delete-btn">X</button>`;

              // ✅ FileDialog로 선택한 파일도 input 요소에 반영
              const dataTransfer = new DataTransfer();
              dataTransfer.items.add(file);
              fileInput.files = dataTransfer.files;

              // ✅ 삭제 버튼 기능 추가
              dropZone.querySelector(".delete-btn").addEventListener("click", function (event) {
                  event.stopPropagation();
                  fileInput.value = ""; // 파일 선택 초기화
                  dropZone.innerHTML = "📂 X-ray 선택"; // 초기 상태로 변경
              });
          };

          reader.readAsDataURL(file);
      }
  }

    // 부모 창에서 실행될 함수 (새 창에서 좌표를 전달받아 콘솔에 출력 및 백엔드로 전송)
  function logFromChild(points) {
    console.log("📌 [부모 창] 최종 좌표 목록:", points);

    const fileInput = document.getElementById("lateral_ceph");
    if (!fileInput.files || fileInput.files.length === 0) {
        alert("⚠️ lateral_ceph에 업로드된 이미지가 없습니다!");
        return;
    }    

    const file = fileInput.files[0]; // ✅ 업로드된 이미지 가져오기
    const formData = new FormData();
    formData.append("image", file); // ✅ 파일 추가
    formData.append("points", JSON.stringify(points)); // ✅ 좌표를 JSON 문자열로 변환하여 추가

    // ✅ 백엔드 요청 (127.0.0.1:9500/draw_psa_line)
    fetch("https://koco.me/draw_psa_line", {
        method: "POST",
        body: formData,
    })
    .then(response => response.blob()) // ✅ 이미지 데이터(blob)로 변환
    .then(blob => {
        console.log("✅ 서버에서 이미지 데이터 수신 완료!");

        // ✅ 이미지 URL 생성
        const imgURL = URL.createObjectURL(blob);

        // ✅ 새 창 열기
        const secondWindow = window.open("", "_blank", "width=800,height=800");
        secondWindow.document.write(`
            <html>
            <head>
                <title>처리된 PSA 이미지</title>
                           
                <style>
                    body { display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f8f8f8; }
                    img { max-width: 100%; max-height: 100%; border: 2px solid black; }
                </style>
            </head>
            <body>
                <img src="${imgURL}" alt="처리된 PSA 이미지">
            </body>
            </html>
        `);

          // ✅ Blob 데이터로부터 File 객체 생성
        const file = new File([blob], "processed_psa.jpg", { type: "image/jpeg" });

        // ✅ PSA 미리보기 박스 가져오기
        const psaBox = document.getElementById("xrayPreview4");
        if (psaBox) {
            psaBox.innerHTML = ""; // 기존 내용 삭제 (초기화)

            // ✅ 새 이미지 요소 생성
            const imgElement = document.createElement("img");
            imgElement.src = URL.createObjectURL(blob);
            imgElement.alt = "처리된 PSA 이미지";
            imgElement.style.width = "100%";
            imgElement.style.height = "100%";
            imgElement.style.objectFit = "cover";

            // ✅ 삭제 버튼 추가
            const deleteBtn = document.createElement("button");
            deleteBtn.innerText = "X";
            deleteBtn.classList.add("delete-btn");
            deleteBtn.addEventListener("click", function () {
                psaBox.innerHTML = "📂 PSA"; // 초기 상태로 되돌리기
                psaInput.value = ""; // 파일도 제거
            });

            

            // ✅ PSA 박스에 추가
            psaBox.appendChild(imgElement);
            psaBox.appendChild(deleteBtn);
        }

        

        // ✅ 파일 입력 필드 (`<input type="file" id="psa">`) 에 추가
        const psaInput = document.getElementById("psa");
        if (psaInput) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file); // 파일 추가
            psaInput.files = dataTransfer.files; // ✅ input 요소에 업로드된 파일처럼 추가
        }
        })
    .catch(error => {
        console.error("🚨 서버 전송 중 오류 발생:", error);
        alert("🚨 서버에 데이터를 전송하는 중 오류가 발생했습니다.");
    });
}


    document.getElementById("drawPSALine").addEventListener("click", (event) => {
        event.preventDefault(); // ✅ 기본 폼 제출 방지

        const fileInput = document.getElementById("lateral_ceph"); // 파일 input 요소
        if (!fileInput.files || fileInput.files.length === 0) {
            alert("⚠️ lateral_ceph에 업로드된 이미지가 없습니다!");
            return;
        }

        const file = fileInput.files[0]; // ✅ FileDialog에서 선택한 파일 가져오기
        const reader = new FileReader();

        reader.onload = function (e) {
            // 새 창 생성 (확대 이미지 창)
            const newWindow = window.open("", "_blank", "width=800,height=800,scrollbars=yes");
            newWindow.name = "firstWindow"; // ✅ 창 이름 설정

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
                                        }
                                    }, 100); // ✅ 빨간 점이 찍힌 후 0.1초 뒤에 알림 표시
                                }
                            });
                        }, 500); // ✅ 실행 보장 (0.5초 딜레이)
                    <\/script>
                </body>
                </html>
            `);
        };

    reader.readAsDataURL(file);
});



    // 4개의 Drop Zone 설정
    setupDropZone("xrayPreview1", "pano");
    setupDropZone("xrayPreview2", "lateral_ceph");
    setupDropZone("xrayPreview3", "frontal_ceph");
    setupDropZone("xrayPreview4", "psa");
    setupDropZone("excelPreview", "excel_data");

    // 8개의 구외포토 Drop Zone 설정 (✅ 추가된 코드)
    for (let i = 1; i <= 8; i++) {
      setupDropZone(`photoPreview${i}`, `photo${i}`);
    }
    // 5개의 구내포토 Drop Zone 설정 (✅ 추가된 코드)
    for (let i = 1; i <= 5; i++) {
      setupDropZone(`oralPhotoPreview${i}`, `oralPhoto${i}`);
    }
    // 4개의 자세포토 Drop Zone 설정 (✅ 추가된 코드)
    for (let i = 1; i <= 8; i++) {
      setupDropZone(`posturePhotoPreview${i}`, `posturePhoto${i}`);
    }

    // 로그 출력 함수
    function logInfo(...args) {
      console.log("[INFO]", ...args);
    }
    function logError(...args) {
      console.error("[ERROR]", ...args);
    }

    

    // 폼 제출 시 이벤트 처리
    document.getElementById("uploadForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      logInfo("FormData 생성 완료:", Object.fromEntries(formData.entries()));
      try {
          const response = await fetch("https://koco.me/dash_board", {
              method: "POST",
              body: formData
          });
          logInfo("서버 응답 상태 코드:", response.status);
          if (!response.ok) {
              throw new Error(`서버 오류 발생: ${response.status}`);
          }
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          logInfo("Blob 객체 생성 완료:", url);
          const selectedFileType = document.getElementById("file_type").value;
          const pdfViewer = document.getElementById("pdfViewer");
          if (selectedFileType === "pdf") {
              pdfViewer.src = url;
              pdfViewer.style.display = "block";
          } else {
              const link = document.createElement("a");
              link.href = url;
              link.download = "output_ppt.pptx";
              document.body.appendChild(link);
              link.click();
              link.remove();
          }
      } catch (error) {
          logError("업로드 중 오류 발생:", error);
          alert("업로드 중 오류가 발생했습니다: " + error.message);
      }
  });






  </script>