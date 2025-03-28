const data = [
  { mean_degree: 81, name: "SNA", value: "", category: "pink" },
  { mean_degree: 79, name: "SNB", value: "", category: "pink" },
  { mean_degree: 91, name: "IMPA", value: "", category: "pink" },
  { mean_degree: 106, name: "1 to SN", value: "", category: "pink" },
  { mean_degree: 27, name: "FMA", value: "", category: "pink" },
  { mean_degree: 27.5, name: "PMA", value: "", category: "pink" },
  { mean_degree: 34, name: "SN-GoMe", value: "", category: "pink" },
  { mean_degree: 81, name: "FA'B'", value: "", category: "pink" },
  { mean_degree: 81, name: "FABA", value: "", category: "pink" },
  { mean_degree: 52, name: "Y-angle", value: "", category: "pink" },
  { mean_degree: 50, name: "UGA", value: "", category: "pink" },
  { mean_degree: 75, name: "LGA", value: "", category: "pink" },
  { mean_degree: 123, name: "S-A", value: "", category: "pink" },
  { mean_degree: 53, name: "UIOP", value: "", category: "pink" },
  { mean_degree: 17, name: "MOP", value: "", category: "pink" },
  { mean_degree: 31, name: "FH<Ans", value: "", category: "pink" },
  { mean_degree: 37, name: "FH<Pr", value: "", category: "pink" },
  { mean_degree: 131, name: "Na-S-BaA", value: "", category: "pink" },
  { mean_length: 3, name: "Incisor Overbite", value: "", category: "green" },
  { mean_length: 3, name: "Incisor Overjet", value: "", category: "green" },
  { mean_degree: 95, name: "NALA", value: "", category: "red" },
  { mean_length: 20, name: "HR", value: "", category: "red" },
  { mean: "없음", name: "Cal", value: "", category: "green" },
  { mean_length: 69, name: "ACBL", value: "", category: "blue" },
  { mean_length: 71, name: "MBL", value: "", category: "blue" },
  { mean_length: null, name: "AFH", value: "", category: "blue" },
  { mean_length: null, name: "PFH", value: "", category: "blue" },
  { mean_length: 0, name: "E-line", value: "", category: "blue" },
  { mean_length: 50, name: "Ramus height", value: "", category: "blue" },
  { mean_length: 0, name: "Naperp-A", value: "", category: "blue" },
  { mean_length: 54, name: "MxBL", value: "", category: "blue" },
  { mean_length: 46, name: "PCBL", value: "", category: "blue" },
  { mean_length: 25, name: "S-Por", value: "", category: "blue" },
];

document.addEventListener("DOMContentLoaded", function () {
  console.log("✅ 테이블 생성 스크립트 로드됨");

  const tooltips = {
    SNA: "Sella-Nasion-A",
    SNB: "Sella-Nasion-B",
    IMPA: "Incisor Mandibular Plane Angle",
    "1 to SN": "1 to Sella-Nasion",
    FMA: "Frankfort Mandibular Plane Angle",
    PMA: "Palatal Mandibular Angle",
    "SN-GoMe": "Sella-Nasion to Gonion-Menton",
    "FA'B'": "Frankfort Horizontal to AB",
    FABA: "Frankfort Horizontal to AB Angle",
    "Y-angle": "Y-axis Angle",
    UGA: "Upper Gonial Angle",
    LGA: "Lower Gonial Angle",
    "S-A": "Sella-A Point",
    UIOP: "Upper Incisor to Occlusal Plane",
    MOP: "Mandibular Plane to Occlusal Plane",
    "FH<Ans": "Frankfort Horizontal to ANS",
    "FH<Pr": "Frankfort Horizontal to Pogonion",
    "Na-S-BaA": "Nasion-Sella-Basion to A",
    "incisor Overbite": "incisor Overbite",
    "incisor Overjet": "incisor Overjet",
    NALA: "Nasion-A Point to Lower A Point",
    HR: "Horizontal Reference",
    Cal: "Calibration",
    ACBL: "Anterior Cranial Base Length",
    MBL: "Mandibular Base Length",
    AFH: "Anterior Face Height",
    PFH: "Posterior Face Height",
    "E-line": "E-line",
    "Ramus height": "Ramus height",
    "Naperp-A": "Nasion perpendicular to A",
    MxBL: "Maxillary Base Length",
    PCBL: "Posterior Cranial Base Length",
    "S-Por": "Sella to Porion",
  };

  function generateTable() {
    const tableContainer = document.getElementById("tableContainer1");
    tableContainer.innerHTML = ""; // ✅ 기존 테이블 초기화

    const table = document.createElement("table");
    table.innerHTML = `
            <thead>
                <tr>
                    <th style="width: 40%;">필수 계측항목</th>
                    <th style="width: 20%;">평균치</th>
                    <th style="width: 20%;">계측값</th>
            </tr>
            </thead>
            <tbody></tbody>
        `;

    const tableBody = table.querySelector("tbody");

    data.forEach((row) => {
      const tr = document.createElement("tr");

      // ✅ `<` 및 `>` 기호 변환
      const safeName = row.name.replace(/</g, "&lt;").replace(/>/g, "&gt;");
      const tip = tooltips[row.name] || "";

      let meanValue = "";
      if (row.mean_degree !== undefined && row.mean_degree !== "") {
        meanValue = `${row.mean_degree} °`;
      } else if (row.mean_length !== undefined && row.mean_length !== "") {
        meanValue = `${row.mean_length} mm`;
      }

      tr.innerHTML = `
                <td class="tooltip ${row.category}" data-tooltip="${tip}">${safeName}</td> <!-- ✅ HTML 엔티티 변환 적용 -->
                <td>${meanValue}</td>               
                <td class="value-cell" data-name="${row.name}">${row.value}</td> <!-- ✅ data-name 속성 유지 -->
            `;
      tableBody.appendChild(tr);
    });

    tableContainer.appendChild(table);
  }

  // // ✅ 테이블 초기 생성
  console.log(
    "📌 container1 존재 여부:",
    document.getElementById("tableContainer1")
  );
  generateTable();
  generateDiagnosisTable();
});

function updateTableWithAngles(angleDictionary) {
  console.log("📌 계측값 업데이트 실행");

  // ✅ 이름 → 단위 맵을 미리 구성 (빠르게 단위 붙이기 위함)
  const unitMap = {};
  data.forEach((row) => {
    if (row.mean_degree !== undefined && row.mean_degree !== "") {
      unitMap[row.name] = " °";
    } else if (row.mean_length !== undefined && row.mean_length !== "") {
      unitMap[row.name] = " mm";
    } else {
      unitMap[row.name] = ""; // 단위 없음
    }
  });

  // ✅ 계측값 셀 찾아서 업데이트

  const container = document.getElementById("tableContainer1");
  const valueCells = container.querySelectorAll(".value-cell");

  valueCells.forEach((cell) => {
    const name = cell.getAttribute("data-name");
    if (name in angleDictionary) {
      const rawValue = angleDictionary[name];
      const unit = unitMap[name] || "";
      cell.textContent = rawValue !== "" ? `${rawValue}${unit}` : "";
    }
  });

  console.log("✅ 계측값 업데이트 완료!");
}

function generateDiagnosisTable() {
  const tableContainer = document.getElementById("tableContainer2");
  if (!tableContainer) {
    console.error("❌ tableContainer2를 찾을 수 없습니다.");
    return;
  }

  const indicators = [
    { name: "HGI", mean: "" },
    { name: "VGI", mean: "" },
    { name: "APDI", mean: "" },
    { name: "ODI", mean: "" },
    { name: "IAPDI", mean: "" },
    { name: "IODI", mean: "" },
    { name: "2APDL", mean: "" },
    { name: "VDL", mean: "" },
    { name: "CFD", mean: "" },
    { name: "EI", mean: "" },
  ];

  const table = document.createElement("table");
  table.innerHTML = `
      <thead>
        <tr>
          <th style="width: 40%;">진단 지표</th>
          <th style="width: 20%;">평균값</th>
          <th style="width: 20%;">결과값</th>
        </tr>
      </thead>
      <tbody></tbody>
    `;

  const tbody = table.querySelector("tbody");

  indicators.forEach((item) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
        <td>${item.name}</td>
        <td>${item.mean}</td>
        <td class="diagnosis-value" data-name="${item.name}"></td>
      `;
    tbody.appendChild(tr);
  });

  tableContainer.appendChild(table);
}

function updateDiagnosisTable(additionalAngles) {
  const cells = document.querySelectorAll(".diagnosis-value");
  cells.forEach((cell) => {
    let name = cell.getAttribute("data-name");

    // ✅ '2APDL' 셀은 'APDL' 키와 연결되도록 예외 처리
    const lookupKey = name === "2APDL" ? "APDL" : name;

    // ✅ matching 되는 값이 있을 경우 셀에 출력
    if (lookupKey in additionalAngles) {
      cell.textContent = additionalAngles[lookupKey];
    }
  });
}
