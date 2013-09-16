$('#dpfrom').datepicker({format: 'yyyy/mm/dd'});
            $('#btn2').click(function(e){
                e.stopPropagation();
                $('#dpfrom').datepicker('update', '03/17/12');
            });   
            
$('#dpto').datepicker({format: 'yyyy/mm/dd'});
            $('#btn2').click(function(e){
                e.stopPropagation();
                $('#dpto').datepicker('update', '03/17/12');
            });              

