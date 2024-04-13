 $(function() {



    $("#map").googleMap({
      zoom: 10, // Initial zoom level (optional)
      coords: [48.895651, 2.290569], // Map center (optional)
      type: "ROADMAP" // Map type (optional)
    });



  alert('Haya Gmap');

   $("#btn1").click(function(){
        $("#test1").text("Hello world!");
    });
    $("#btn2").click(function(){
        $("#test2").html("Hello world!");
    });
    $("#btn3").click(function(){
        $("#test3").val("Dolly Duck");
    });



  })