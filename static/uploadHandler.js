function dataURLtoBlob(dataURL) {
  const arr = dataURL.split(",");
  const mime = arr[0].match(/:(.*?);/)[1]; // MIME 타입 추출
  const bstr = atob(arr[1]); // Base64 디코딩
  let n = bstr.length;
  const u8arr = new Uint8Array(n);

  while (n--) {
    u8arr[n] = bstr.charCodeAt(n);
  }

  return new Blob([u8arr], { type: mime });
}

document.querySelectorAll(".file-preview").forEach((preview) => {
  const bg = preview.style.backgroundImage;
  preview.style.backgroundImage = "none"; // 배경 제거
  preview.style.position = "relative";

  const overlay = document.createElement("div");
  overlay.style.position = "absolute";
  overlay.style.inset = 0;
  overlay.style.backgroundImage = bg;
  overlay.style.backgroundSize = "cover";
  overlay.style.backgroundPosition = "center";
  overlay.style.opacity = "0.8"; // 투명도 조절
  overlay.style.filter = "brightness(0.6)"; // ✅ blur 제거!
  overlay.style.zIndex = "-1";

  preview.appendChild(overlay);
});

document.addEventListener("DOMContentLoaded", function () {
  // 파일 업로드 처리
  function handleFilePreview(fileInput, dropZone) {
    const file = fileInput.files[0];

    if (file) {
      const reader = new FileReader();

      reader.onload = (e) => {
        dropZone.innerHTML = `<img src="${e.target.result}" alt="미리보기">
                                      <button class="delete-btn">X</button>`;

        dropZone
          .querySelector(".delete-btn")
          .addEventListener("click", (event) => {
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
    fileInput.addEventListener("change", () =>
      handleFilePreview(fileInput, dropZone)
    );

    dropZone.addEventListener("dragover", (e) => {
      console.log("🔥 dragover event fired!");
      e.preventDefault();
      dropZone.classList.add("drag-over");
    });

    dropZone.addEventListener("dragleave", () =>
      dropZone.classList.remove("drag-over")
    );

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

  $("#drawPSALine").on("click", function (event) {
    event.preventDefault();

    const fileInput = $("#lateral_ceph")[0];

    if (!fileInput.files.length) {
      alert("⚠️ lateral_ceph에 업로드된 이미지가 없습니다!");
      return;
    }

    const file = fileInput.files[0];
    const reader = new FileReader();

    reader.onload = function (e) {
      const imageData = e.target.result;

      // ✅ 새 창 열기
      const newWindow = window.open(
        "/static/psa.html",
        "_blank",
        "width=700,height=700,scrollbars=yes"
      );

      // ✅ 새 창이 완전히 열린 후에 postMessage 전달
      newWindow.onload = function () {
        console.log("✅ 새 창이 로드됨!");
        newWindow.postMessage({ type: "PSA_IMAGE", data: imageData }, "*");
        console.log("✅ 이미지 데이터를 새 창으로 전송 완료!");
      };
    };

    reader.readAsDataURL(file); // base64로 읽기
  });

  //drawPSOline 버튼 클릭시 alert창 띄우기
  $("#drawPSOLine").on("click", function (event) {
    event.preventDefault();
    alert("개발 중입니다.");
  });

  $(document).ready(function () {
    $("#excel-create-btn").on("click", function (event) {
      event.preventDefault();
      console.log("🔥 PSA 엑셀 생성 버튼 클릭됨!");

      const fileInput = $("#lateral_ceph")[0];

      // ✅ 파일이 없는 경우 경고
      if (!fileInput.files.length) {
        alert("⚠️ lateral_ceph에 업로드된 이미지가 없습니다!");
        return;
      }

      const file = fileInput.files[0];
      console.log("📂 파일 선택됨:", file);

      const reader = new FileReader();

      reader.onload = function (e) {
        const imageData = e.target.result;
        console.log("🔥 파일 읽기 완료!");

        // ✅ 새 창 열기
        const newWindow = window.open(
          "/static/create_excel.html",
          "_blank",
          "width=700,height=700,scrollbars=yes"
        );

        // ✅ 새 창이 로드된 후 이미지 데이터 전달
        newWindow.onload = function () {
          newWindow.postMessage({ type: "PSA_IMAGE", data: imageData }, "*");
          console.log("✅ 이미지 데이터를 create_excel1.html로 전송 완료!");
        };
      };

      reader.readAsDataURL(file); // ✅ Base64 문자열로 읽기
    });
  });

  //Drop Zone 설정
  setupDropZone("xrayPreview1", "pano");
  setupDropZone("xrayPreview2", "lateral_ceph");
  setupDropZone("xrayPreview3", "frontal_ceph");
  setupDropZone("xrayPreview4", "psa");
  setupDropZone("excelPreview", "excel_data");

  for (let i = 1; i <= 8; i++) setupDropZone(`photoPreview${i}`, `photo${i}`);
  for (let i = 1; i <= 5; i++)
    setupDropZone(`oralPhotoPreview${i}`, `oralPhoto${i}`);
  for (let i = 1; i <= 8; i++)
    setupDropZone(`posturePhotoPreview${i}`, `posturePhoto${i}`);
});
