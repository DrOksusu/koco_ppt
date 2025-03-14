function calculateAngle(landmarkCoordinates, key1, key2, key3) {
    /**
     * 세 개의 랜드마크 키를 받아 key2를 기준으로 내각을 계산하는 함수
     * 
     * @param {Object} landmarkCoordinates - 좌표를 저장한 딕셔너리
     * @param {string} key1 - 첫 번째 랜드마크 (예: "Sella")
     * @param {string} key2 - 기준이 되는 두 번째 랜드마크 (예: "Nasion")
     * @param {string} key3 - 세 번째 랜드마크 (예: "A-Point")
     * @returns {number} - 내각 (°) 값 (소수점 둘째 자리 반올림)
     */

    // ✅ 1. 입력된 키가 딕셔너리에 있는지 확인
    if (!(key1 in landmarkCoordinates) || !(key2 in landmarkCoordinates) || !(key3 in landmarkCoordinates)) {
        console.error("❌ 입력된 키가 landmarkCoordinates에 존재하지 않습니다!");
        return null;
    }

    // ✅ 2. 좌표 가져오기
    const point1 = landmarkCoordinates[key1];  // 첫 번째 점
    const point2 = landmarkCoordinates[key2];  // 기준점 (각도의 꼭짓점)
    const point3 = landmarkCoordinates[key3];  // 세 번째 점

    // ✅ 3. 벡터 계산 (P2 -> P1, P2 -> P3)
    const vector1 = { x: point1.x - point2.x, y: point1.y - point2.y };
    const vector2 = { x: point3.x - point2.x, y: point3.y - point2.y };

    // ✅ 4. 벡터 내적(점곱) 계산
    const dotProduct = (vector1.x * vector2.x) + (vector1.y * vector2.y);

    // ✅ 5. 벡터 크기(길이) 계산
    const magnitude1 = Math.sqrt(vector1.x ** 2 + vector1.y ** 2);
    const magnitude2 = Math.sqrt(vector2.x ** 2 + vector2.y ** 2);

    // ✅ 6. 코사인 법칙을 사용하여 내각(°) 계산
    const cosTheta = dotProduct / (magnitude1 * magnitude2);
    const thetaRad = Math.acos(Math.min(Math.max(cosTheta, -1), 1));  // -1 ~ 1 범위로 제한
    const thetaDeg = (thetaRad * 180) / Math.PI;

    return Math.round(thetaDeg * 100) / 100;  // ✅ 소수점 둘째 자리 반올림
}

function calculateIntersectionAngle(landmarkCoordinates, key1, key2, key3, key4) {
    /**
     * 4개의 랜드마크 키를 받아, 두 직선이 이루는 내각을 계산하는 함수
     * 
     * @param {Object} landmarkCoordinates - 좌표를 저장한 딕셔너리
     * @param {string} key1 - 첫 번째 직선의 시작점 (예: "Sella")
     * @param {string} key2 - 첫 번째 직선의 끝점이자 두 번째 직선의 시작점 (예: "Nasion")
     * @param {string} key3 - 두 번째 직선의 끝점이자 첫 번째 직선과 연결된 점 (예: "Nasion")
     * @param {string} key4 - 두 번째 직선의 끝점 (예: "A-Point")
     * @returns {number|null} - 내각 (°) 값 (소수점 둘째 자리 반올림) 또는 null (잘못된 입력)
     */

    // ✅ 1. 입력된 키가 딕셔너리에 있는지 확인
    if (!(key1 in landmarkCoordinates) || !(key2 in landmarkCoordinates) || 
        !(key3 in landmarkCoordinates) || !(key4 in landmarkCoordinates)) {
        console.error("❌ 입력된 키가 landmarkCoordinates에 존재하지 않습니다!");
        return null;
    }

    // ✅ 2. 좌표 가져오기
    const point1 = landmarkCoordinates[key1]; // 첫 번째 직선의 시작점
    const point2 = landmarkCoordinates[key2]; // 첫 번째 직선의 끝점이자 두 번째 직선의 시작점
    const point3 = landmarkCoordinates[key3]; // 두 번째 직선의 시작점 (key2와 같아야 함)
    const point4 = landmarkCoordinates[key4]; // 두 번째 직선의 끝점

    // ✅ 3. 벡터 계산 (P1 -> P2, P3 -> P4)
    const vector1 = { x: point2.x - point1.x, y: point2.y - point1.y }; // 벡터 1 (직선 1)
    const vector2 = { x: point4.x - point3.x, y: point4.y - point3.y }; // 벡터 2 (직선 2)

    // ✅ 4. 벡터 내적(점곱) 계산
    const dotProduct = (vector1.x * vector2.x) + (vector1.y * vector2.y);

    // ✅ 5. 벡터 크기(길이) 계산
    const magnitude1 = Math.sqrt(vector1.x ** 2 + vector1.y ** 2);
    const magnitude2 = Math.sqrt(vector2.x ** 2 + vector2.y ** 2);

    // ✅ 6. 코사인 법칙을 사용하여 내각(°) 계산
    const cosTheta = dotProduct / (magnitude1 * magnitude2);
    const thetaRad = Math.acos(Math.min(Math.max(cosTheta, -1), 1));  // -1 ~ 1 범위로 제한
    const thetaDeg = (thetaRad * 180) / Math.PI;

    return Math.round(thetaDeg * 100) / 100;  // ✅ 소수점 둘째 자리 반올림
}


// ✅ SNA & SNB 계산 후 딕셔너리 반환 함수
function getAngleDictionary(landmarkCoordinates) {
    /**
     * SNA 및 SNB 내각을 계산하고 딕셔너리 형태로 반환하는 함수.
     *
     * @param {Object} landmarkCoordinates - 좌표를 저장한 딕셔너리
     * @returns {Object} - {"SNA": xx.x, "SNB": xx.x} 형태의 객체
     */

    const angles = {
        SNA: calculateAngle(landmarkCoordinates, "Sella", "Nasion", "A-Point"),
        SNB: calculateAngle(landmarkCoordinates, "Sella", "Nasion", "B-Point"),
        FMA: calculateIntersectionAngle(landmarkCoordinates, "Porion", "Orbitale", "Menton","Go"),
        '1 to SN': calculateIntersectionAngle(landmarkCoordinates, "Sella", "Nasion", "Mx.1 cr", "Mx.1 root"),
        IMPA : calculateIntersectionAngle(landmarkCoordinates, "Go", "Menton", "Mn.1 cr", "Mn.1 root"),
        PMA : calculateIntersectionAngle(landmarkCoordinates, "Porion", "Orbitale", "Go", "Menton"),
        'SN-GoMe' : calculateIntersectionAngle(landmarkCoordinates, "Sella", "Nasion", "Go", "Menton"),
        "FA'B'" : calculateIntersectionAngle(landmarkCoordinates, "Porion", "Orbitale", "soft tissue A", "soft tissue B"),
        "FABA" : calculateIntersectionAngle(landmarkCoordinates, "Porion", "Orbitale", "A-Point", "B-Point"),
        "Y-angle" : calculateAngle(landmarkCoordinates, "Porion", "Orbitale", "Gn"),
        "UGA" : calculateAngle(landmarkCoordinates, "Ar", "Go", "Nasion"),
        "LGA" : calculateAngle(landmarkCoordinates, "Nasion", "Go", "Menton"),
        "S-A" : calculateAngle(landmarkCoordinates, "Nasion", "Sella", "Ar"),
        "UIOP" : calculateIntersectionAngle(landmarkCoordinates, "Mn.1 cr", "Mn.6 distal", "Mx.1 cr", "Mx.1 root"),
        "MOP" : calculateIntersectionAngle(landmarkCoordinates, "Mn.6 distal", "Mn.1 cr", "Menton", "Go"),
        "FH<Ans" :calculateIntersectionAngle(landmarkCoordinates, "Porion", "Orbitale", "Sella", "ANS"),
        "FH<Pr" : calculateIntersectionAngle(landmarkCoordinates, "Porion", "Orbitale", "Sella", "Porion"),
        "Na-S-BaA" : calculateAngle(landmarkCoordinates, "Nasion", "Sella", "Basion"),
        "NALA" : calculateAngle(landmarkCoordinates, "Columella", "Subnasale", "soft tissue A"),


        

    };

    console.log("📌 계산된 각도들:", angles);
    return angles;
}

