function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $("#form-house").submit(function(e){
        e.preventDefault();
        $(this).ajaxSubmit({
            url:'/app/newhouse/',
            type:'POST',
            dataType:'json',
            success:function(data){
                if(data.code == '200'){
                    $('#form-house').hide()
                    $('#form-house-image').css('display','block')
                }
            }
        })
    })

    $("#form-house-image").submit(function(e){
        e.preventDefault();
        $(this).ajaxSubmit({
            url:'/app/house_image/',
            type:'POST',
            dataType:'json',
            success:function(data){
                if(data.code == '200'){
                    alert('上传成功,可继续上传房屋图片')
//                    $("#form-house-image").load(location.href+" #form-house-image")
                    $('#form-house-image').css('display','block')
                }
            }
        })
    })
})