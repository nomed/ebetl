//turn to inline mode
//$.fn.editable.defaults.mode = 'inline';

$('#qty a#qta').editable({
    type: 'text',
    name: 'qta',
    url: '/post',
    title: 'Enter QTY',

    success: function(response, newValue) {
        data = $.parseJSON(response);
        strid = 'cost'+data.pk 
        //document.getElementById(strid).innerHTML = data.costo
        strid = 'totale_qta'+data.pk 
        document.getElementById(strid).innerHTML = data.totale_qta   
        //strid = 'totale_costo'+data.pk 
        //document.getElementById(strid).innerHTML = "<b>"+data.totale_costo+"</b>"              
        console.log(data)        
        }  
});

$('#qty a#qtaconf').editable({
    type: 'text',
    name: 'qtaconf',
    url: '/post',
    title: 'Enter QTY',
    
    success: function(response, newValue) {
        data = $.parseJSON(response);
        strid = 'cost'+data.pk 
        document.getElementById(strid).innerHTML = data.costo
        strid = 'totale_qta'+data.pk 
        document.getElementById(strid).innerHTML = data.totale_qta   
        strid = 'totale_costo'+data.pk 
        document.getElementById(strid).innerHTML = "<b>"+data.totale_costo+"</b>"
        console.log(data)    
        }  
    
});

$('#cost a#costo2').editable({
    type: 'text',
    name: 'costo2',
    url: '/post',
    title: 'Enter QTY',

    success: function(response, newValue) {
        data = $.parseJSON(response);
        //strid = 'cost2'+data.pk 
        //document.getElementById(strid).innerHTML = data.costo2        
        console.log(data)        
        }  
});


//$(function () {
//    $('#fileupload').fileupload({
//        dataType: 'json',
//        done: function (e, data) {
//            $.each(data.result.files, function (index, file) {
//                $('<p/>').text(file.name).appendTo(document.body);
//            });
//        }
//    });
//});



