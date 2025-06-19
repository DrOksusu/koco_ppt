$(document).ready(function(){
   



  //결제하기 버튼 클릭 이벤트
  $("#pay-button").click(async function(){

      const method = $(".method-radio:checked").val();


      const response = await Bootpay.requestPayment({
          "application_id": "6694c19e245b30e3f436724d",
          "price": 100,
          "order_name": "노트북",
          "order_id": "TEST_ORDER_ID",
          "pg": "토스",
          "method":method,
          "tax_free": 0,
          "user": {
            "id": "회원아이디",
            "username": "회원이름",
            "phone": "01000000000",
            "email": "test@test.com"
          },
          "items": [
            {
              "id": "item_id",
              "name": "노트북",
              "qty": 100,
              "price": 1
            }
          ],
          "extra": {
            "open_type": "iframe",
            "card_quota": "0,2,3",
            "escrow": false
          }
        });

        console.log("===결제완료=====");
        console.log(response);
  });


});
