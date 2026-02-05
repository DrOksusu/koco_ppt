console.log("📢 uploadHandler.js 로딩됨!");

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

window.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("token");
  if (token) {
    try {
      const res = await fetch("http://3.37.159.141:8080/verify-token", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`, // ✅ 헤더에 토큰 포함
        },
      });

      const result = await res.json();

      if (res.ok) {
        console.log("✅ 자동 로그인 성공:", result.user);
        // 여기서 사용자 정보를 화면에 띄우거나, 메인 페이지로 이동 가능
      } else {
        console.log("❌ 토큰 만료 또는 무효, 다시 로그인 필요");
        localStorage.removeItem("token"); // 잘못된 토큰 제거
      }
    } catch (err) {
      console.error("자동 로그인 요청 실패:", err);
    }
  } else {
    console.log("🔑 저장된 토큰 없음. 로그인 필요.");
  }
});

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

    let clickTimer = null;

    dropZone.addEventListener("click", (e) => {
      console.log("🖱️ click 이벤트 발생");

      // 이미 타이머가 있다면 → 더블클릭으로 판단
      if (clickTimer) {
        clearTimeout(clickTimer);
        clickTimer = null;
        console.log("💥 더블클릭으로 판단됨 → 파일창 열지 않음");
        return;
      }

      // 클릭 후 300ms 안에 또 클릭 들어오면 → 더블클릭으로 판단
      clickTimer = setTimeout(() => {
        console.log("✅ 단일 클릭 → 파일창 열기");
        fileInput.click(); // 👉 여기서만 실제 파일창 열림
        clickTimer = null;
      }, 300); // 300ms 이내에 또 클릭이 들어오면 cancel
    });

    dropZone.addEventListener("dblclick", (e) => {
      e.preventDefault();
      e.stopPropagation();
      console.log("🔥 dblclick 이벤트 실행됨!");

      const img = dropZone.querySelector("img");
      if (!img || !img.src) {
        console.warn("📭 이미지가 없습니다. 확대 안 함");
        return;
      }

      const popup = window.open(
        "",
        "_blank",
        "width=1000,height=800,resizable=yes,scrollbars=no"
      );

      popup.document.write(`
          <!DOCTYPE html>
          <html lang="ko">
          <head>
            <meta charset="UTF-8">
            <title>확대 이미지</title>
            <style>
              html, body {
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                background: black;
                display: flex;
                justify-content: center;
                align-items: center;
              }
              img {
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
              }
            </style>
          </head>
          <body>
            <img src="${img.src}" alt="확대 이미지" />
          </body>
          </html>
        `);
    });

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

    // ✅✅✅ 수정됨: 파일 input이 직접 변경되었을 때도 미리보기 반영
    fileInput.addEventListener("change", () => {
      handleFilePreview(fileInput, dropZone);
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
        "width=700,height=600,scrollbars=yes"
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
        "/static/pso.html",
        "_blank",
        "width=800,height=700,scrollbars=yes"
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

    // frontalCeph 버튼 클릭 시 처리
    $("#drawFrontalLine").on("click", function (event) {
      event.preventDefault(); // 기본 동작 방지

      const fileInput = $("#frontal_ceph")[0];

      // ✅ 파일 없을 경우 경고창
      if (!fileInput.files.length) {
        alert("⚠️ frontal_ceph에 업로드된 이미지가 없습니다!");
        return;
      }

      const file = fileInput.files[0];
      const reader = new FileReader();

      // ✅ base64로 이미지 읽기
      reader.onload = function (e) {
        const imageData = e.target.result;

        // ✅ 새 창 열기
        const newWindow = window.open(
          "/static/frontal_ceph.html", // 👉 이 HTML 파일이 서버에 있어야 해!
          "_blank",
          "width=800,height=900,scrollbars=yes"
        );

        // ✅ 새 창 로드된 후 이미지 전송
        newWindow.onload = function () {
          console.log("✅ frontal_ceph 창 로드됨!");
          newWindow.postMessage({ type: "FRONTAL_CEPH_IMAGE", data: imageData }, "*");
          console.log("✅ 이미지 데이터를 frontal_ceph.html로 전송 완료!");
        };
      };

      reader.readAsDataURL(file); // ✅ base64로 읽기 시작
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
  setupDropZone("xrayPreview5", "landmarks"); // 📂 Landmarks도 빠져있음
  setupDropZone("xrayPreview6", "pso"); // 📂 PSO 여기 추가!!

  setupDropZone("excelPreview", "excel_data");

  for (let i = 1; i <= 8; i++) setupDropZone(`photoPreview${i}`, `photo${i}`);
  for (let i = 1; i <= 5; i++)
    setupDropZone(`oralPhotoPreview${i}`, `oralPhoto${i}`);
  for (let i = 1; i <= 8; i++)
    setupDropZone(`posturePhotoPreview${i}`, `posturePhoto${i}`);
});

// landmark_rightclick.js
