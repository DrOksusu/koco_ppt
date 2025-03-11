document.addEventListener("DOMContentLoaded", function () {
    // 파일 업로드 처리
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

    // 드롭존 설정
    function setupDropZone(dropZoneId, fileInputId) {
        const dropZone = document.getElementById(dropZoneId);
        const fileInput = document.getElementById(fileInputId);

        if (!dropZone || !fileInput) return;

        dropZone.addEventListener("click", () => fileInput.click());
        fileInput.addEventListener("change", () => handleFilePreview(fileInput, dropZone));

        dropZone.addEventListener("dragover", (e) => {
            console.log("🔥 dragover event fired!");
            e.preventDefault();
            dropZone.classList.add("drag-over");
            
        });

        dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));

        dropZone.addEventListener("drop", (e) => {
            console.log("🔥 drop event fired!");
            e.preventDefault();
            dropZone.classList.remove("drag-over");

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFilePreview(fileInput, dropZone);
            }
        });
    }

    $(document).ready(function () {
        $("#drawPSALine").on("click", function (event) {
            event.preventDefault();
            console.log("🔥 PSA 선 그리기 버튼 클릭됨!");
    
            let fileInput = $("#lateral_ceph")[0];
    
            // ✅ 1. `fileInput.files`가 비어있다면 `localStorage`에서 복구
            if (!fileInput.files.length) {
                console.warn("⚠️ `fileInput.files`이 비어 있음. localStorage에서 복구 시도");
                const storedFile = localStorage.getItem("psaFile");
                if (storedFile) {
                    console.log("✅ localStorage에서 `psaFile` 복구됨!");
                    const blob = dataURLtoBlob(storedFile);
                    const file = new File([blob], "lateral_ceph.jpg", { type: "image/jpeg" });
    
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    fileInput.files = dataTransfer.files; // ✅ 파일 복원
                }
            }
    
            // ✅ 2. 파일이 여전히 없으면 경고
            if (!fileInput.files.length) {
                alert("⚠️ lateral_ceph에 업로드된 이미지가 없습니다!");
                return;
            }
    
            const file = fileInput.files[0];
            console.log("📂 PSA 선 그리기 파일 정보:", file);
            const reader = new FileReader();
    
            reader.onload = function (e) {
                console.log("🔥 파일 읽기 완료!");
    
                // ✅ 3. Base64 인코딩된 이미지 데이터를 localStorage에 저장
                localStorage.setItem("psaImage", e.target.result);
                localStorage.setItem("psaFile", e.target.result); // ✅ 파일 정보도 저장
                console.log("🔥 PSA 선 그리기 이미지 데이터 저장 완료!");
    
                // ✅ 4. `psa.html` 새 창 열기
                window.open("/static/psa.html", "_blank", "width=700,height=700,scrollbars=yes");
            };
    
            reader.readAsDataURL(file);
        });
    });
    

    $(document).ready(function () {
        $("#excel-create-btn").on("click", function (event) {
            event.preventDefault();
            console.log("📂 엑셀 데이터 생성 버튼 클릭됨!");
    
            const fileInput = $("#lateral_ceph")[0];
            if (!fileInput.files.length) {
                alert("⚠️ lateral_ceph에 업로드된 이미지가 없습니다!");
                return;
            }
    
            const file = fileInput.files[0];
            console.log("📂 파일 정보:", file);
            const reader = new FileReader();
    
            reader.onload = function (e) {
                console.log("🔥 파일 읽기 완료!");
    
                // ✅ localStorage에 이미지 데이터 저장
                localStorage.setItem("excelImage1", e.target.result);
                console.log("🔥 이미지 데이터 저장 완료!");
    
                // ✅ 새 창 열기
                window.open("/static/create_excel.html", "_blank", "width=700,height=700,scrollbars=yes");
            };
            
    
            reader.readAsDataURL(file);
        });
    });
    

     //Drop Zone 설정
     setupDropZone("xrayPreview1", "pano");
     setupDropZone("xrayPreview2", "lateral_ceph");
     setupDropZone("xrayPreview3", "frontal_ceph");
     setupDropZone("xrayPreview4", "psa");
     setupDropZone("excelPreview", "excel_data");
 
     for (let i = 1; i <= 8; i++) setupDropZone(`photoPreview${i}`, `photo${i}`);
     for (let i = 1; i <= 5; i++) setupDropZone(`oralPhotoPreview${i}`, `oralPhoto${i}`);
     for (let i = 1; i <= 8; i++) setupDropZone(`posturePhotoPreview${i}`, `posturePhoto${i}`);
      
     
});