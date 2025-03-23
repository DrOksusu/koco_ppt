document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ 테이블 생성 스크립트 로드됨");

    const tooltips = {
        "SNA": "Sella-Nasion-A",
        "SNB": "Sella-Nasion-B",
        "IMPA": "Incisor Mandibular Plane Angle",
        "1 to SN": "1 to Sella-Nasion",
        "FMA": "Frankfort Mandibular Plane Angle",
        "PMA": "Palatal Mandibular Angle",
        "SN-GoMe": "Sella-Nasion to Gonion-Menton",
        "FA'B'": "Frankfort Horizontal to AB",
        "FABA": "Frankfort Horizontal to AB Angle",
        "Y-angle": "Y-axis Angle",
        "UGA": "Upper Gonial Angle",
        "LGA": "Lower Gonial Angle",
        "S-A": "Sella-A Point",
        "UIOP": "Upper Incisor to Occlusal Plane",
        "MOP": "Mandibular Plane to Occlusal Plane",
        "FH<Ans": "Frankfort Horizontal to ANS",
        "FH<Pr": "Frankfort Horizontal to Pogonion",
        "Na-S-BaA": "Nasion-Sella-Basion to A",
        "incisor Overbite": "incisor Overbite",
        "incisor Overjet": "incisor Overjet",
        "NALA": "Nasion-A Point to Lower A Point",
        "HR": "Horizontal Reference",
        "Cal": "Calibration",
        "ACBL": "Anterior Cranial Base Length",
        "MBL": "Mandibular Base Length",
        "AFH": "Anterior Face Height",
        "PFH": "Posterior Face Height",
        "E-line": "E-line",
        "Ramus height": "Ramus height",
        "Naperp-A": "Nasion perpendicular to A",
        "MxBL": "Maxillary Base Length",
        "PCBL": "Posterior Cranial Base Length",
        "S-Por": "Sella to Porion"
    };        


    const data = [
        { mean: 81, name: "SNA", value: "", category: "pink" },
        { mean: 79, name: "SNB", value: "", category: "pink" },
        { mean: 91, name: "IMPA", value: "", category: "pink" },
        { mean: 106, name: "1 to SN", value: "", category: "pink" },
        { mean: 27, name: "FMA", value: "", category: "pink" },
        { mean: 27.5, name: "PMA", value: "", category: "pink" },
        { mean: 34, name: "SN-GoMe", value: "", category: "pink" },
        { mean: 81, name: "FA'B'", value: "", category: "pink" },
        { mean: 81, name: "FABA", value: "", category: "pink" },
        { mean: 52, name: "Y-angle", value: "", category: "pink" },
        { mean: 50, name: "UGA", value: "", category: "pink" },
        { mean: 75, name: "LGA", value: "", category: "pink" },
        { mean: 123, name: "S-A", value: "", category: "pink" },
        { mean: 53, name: "UIOP", value: "", category: "pink" },
        { mean: 17, name: "MOP", value: "", category: "pink" },
        { mean: 31, name: "FH<Ans", value: "", category: "pink" },
        { mean: 37, name: "FH<Pr", value: "", category: "pink" },
        { mean: 131, name: "Na-S-BaA", value: "", category: "pink" },
        { mean: 3, name: "Incisor Overbite", value: "", category: "green" },
        { mean: 3, name: "Incisor Overjet", value: "", category: "green" },
        { mean: 95, name: "NALA", value: "", category: "red" },
        { mean: "", name: "HR", value: "", category: "red" },
        { mean: "", name: "Cal", value: "", category: "green" },
        { mean: 69, name: "ACBL", value: "", category: "blue" },
        { mean: 71, name: "MBL", value: "", category: "blue" },
        { mean: "", name: "AFH", value: "", category: "blue" },
        { mean: "", name: "PFH", value: "", category: "blue" },
        { mean: 0, name: "E-line", value: "", category: "blue" },
        { mean: 50, name: "Ramus height", value: "", category: "blue" },
        { mean: 0, name: "Naperp-A", value: "", category: "blue" },
        { mean: 54, name: "MxBL", value: "", category: "blue" },
        { mean: 46, name: "PCBL", value: "", category: "blue" },
        { mean: 25, name: "S-Por", value: "", category: "blue" }
    ];

    function generateTable() {
        const tableContainer = document.getElementById("tableContainer");
        tableContainer.innerHTML = ""; // ✅ 기존 테이블 초기화
    
        const table = document.createElement("table");
        table.innerHTML = `
            <thead>
                <tr>
                    <th>평균치</th>
                    <th>필수 계측항목</th>
                    <th>계측값</th>
                </tr>
            </thead>
            <tbody></tbody>
        `;
    
        const tableBody = table.querySelector("tbody");
    
        data.forEach(row => {
            const tr = document.createElement("tr");
    
            // ✅ `<` 및 `>` 기호 변환
            const safeName = row.name.replace(/</g, "&lt;").replace(/>/g, "&gt;");

            const tip = tooltips[row.name] || "";
    
            tr.innerHTML = `
                <td>${row.mean}</td>
                
                <td class="tooltip ${row.category}" data-tooltip="${tip}">${safeName}</td> <!-- ✅ HTML 엔티티 변환 적용 -->
                <td class="value-cell" data-name="${row.name}">${row.value}</td> <!-- ✅ data-name 속성 유지 -->
            `;
            tableBody.appendChild(tr);
        });
    
        tableContainer.appendChild(table);
    }
    

    

    // // ✅ 테이블 초기 생성
    generateTable();
});

// ✅ 부모 창의 테이블에서 '계측값' 업데이트 함수
function updateTableWithAngles(angleDictionary) {
    console.log("📌 계측값 업데이트 실행");

    // ✅ 모든 '계측값' 셀을 찾고, `data-name`을 기반으로 값 업데이트
    const valueCells = document.querySelectorAll(".value-cell");
    valueCells.forEach(cell => {
        const name = cell.getAttribute("data-name"); // ✅ 계측항목 이름 가져오기
        if (name in angleDictionary) {
            cell.textContent = angleDictionary[name]; // ✅ `angleDictionary` 값으로 업데이트
        }
    });

    console.log("✅ 테이블 업데이트 완료!");
}

