var multiSelectCss = '<style id="multiSelectCss" type="text/css">.multi-select-box{position:relative;display:inline-block}.multi-select-div{position:absolute;z-index:9;background:#fff;border:1px solid #dedede;box-sizing:border-box;max-height:200px;overflow:auto;display:none;}.multi-select-name{padding-left:3px;box-sizing:border-box;padding-right:17px;border:1px solid #dedede;background:#fff url(xl2.jpg) no-repeat right center / 16px 100%}.multi-select-option{margin:0;padding:0}.multi-select-option label{display:block;line-height: 18px;padding:5px}.multi-select-option label:hover{background:#f1f2f6}.multi-select-option input{float:left;margin:3px 3px 0 0}.multi-select-option span{margin-left:22px;display:block}</style>';
function initCss(){
	if($('#multiSelectCss')[0]){
		return false;
	}
	$(document).on('click','body',function(event){
		if(!$(event.target).closest('.multi-select-box')[0] && !$(event.target).closest('.multi-select-div')[0]){
			$('.multi-select-div').slideUp(200,function(){
				$(this).remove();
			});
		}
	});
	$('head').append(multiSelectCss);
}
$.fn.multiSelect = function(options){
	var defaultOptions = {
		zIndex: 9,
	};
	var _options = {};
	//可以加入拓展，参数设置，例如zindex，width，height，color，bgcolor……等UI控制
	initCss();
	this.each(function(){
		var width = $(this).outerWidth();
		var height = $(this).outerHeight();
		var left = $(this).offset().left;
		var top = $(this).offset().top;
		$(this).hide();
		var $parent = $(this).parent();
		if(!$parent.hasClass('.multi-select-box')){
			var parent = '<div class="multi-select-box">\n'
						+	'<input class="multi-select-name" readonly style="width:'+width+'px;height:'+height+'px;" type="text" name="'+this.name+'">\n'
						+'</div>';
			$(this).wrap(parent);
			this.name = 'select-'+this.name;
			$parent = $(this).parent();
		}else{
			return false;
		}
		var _this = this;					
		
		$parent.find('.multi-select-name').click(function(){
			$('.multi-select-div').remove();

			var val = $(this).data('values'), arr = [], oarr = {};
			if(!!val){
				arr = val.split(',');
				for(var i = 0; i < arr.length; i++){
					oarr[arr[i]] = arr[i];
				}
			}
			console.log(oarr)
			var $simulation = $('<div class="multi-select-div" style="width:'+width+'px;left:'+left+'px;top:'+(top+height-1)+'px"></div>');
			$('body').append($simulation);
			var options = '';
			$(_this).find('option').each(function(){
				if($(this).attr('value')){
					options += '<p class="multi-select-option">\n'
							+		'<label>\n'
							+			'<input type="checkbox" '+(oarr[$(this).attr('value')] == $(this).attr('value') ? 'checked' : '')+' data-text="'+$(this).text()+'" value="'+$(this).attr('value')+'"><span>'+$(this).text()+'</span>\n'
							+		'</label>\n'
							+	'</p>';
					
				}
			});
			$simulation.append(options);
			$simulation.slideDown(200);

			$simulation.on('change','input[type="checkbox"]',function(){
				var values = [], texts = [];
				$simulation.find('input[type="checkbox"]:checked').each(function(){
					var value = this.value;
					var text = $(this).data('text');
					values.push(value);
					texts.push(text);
				});
				$parent.find('.multi-select-name').val(texts.toString()).data('values',values.toString());
			});
		});
	});
}
