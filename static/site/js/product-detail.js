function check_status(pk){
	$.ajax({
		url:'/products/'+pk+'/chkst/',
		dataType: 'json',
		success: function(r) {
			if (!r.status) alert();
			console.log(r.d + r.c+r.m);
			var ok = 'OK'; incom = 'INCOMPLETE';
			var suc = 'label label-success ind span1';
			var war = 'label label-warning ind span1';
			$('.nav-list a').each(function(i,v){
				if ($(v).text().indexOf('Detail')>-1){
					if(r.d){
						$(v).find('span').text(ok)
							.removeClass().addClass(suc)
					}else{
						$(v).find('span').text(incom)
							.removeClass().addClass(war)
					}
				}
				if ($(v).text().indexOf('Category')>-1){
					if(r.c){
						$(v).find('span').text(ok)
							.removeClass().addClass(suc)
					}else{
						$(v).find('span').text(incom)
							.removeClass().addClass(war)
					}
				}
				if ($(v).text().indexOf('Target Market')>-1){
					if(r.m){
						$(v).find('span').text(ok)
							.removeClass().addClass(suc)
					}else{
						$(v).find('span').text(incom)
							.removeClass().addClass(war)
					}
				}
			});
		}
	});
}
function toggleCatEdit(e, pk){
	if ($(e).text() == "Save"){
		$(e).text('Edit');
		$('#category input,#category select,#attributes select').attr('disabled', 'disabled');
		var category = $('#segment').val() + ':' + $('#family').val() + ':'
					+ $('#classes').val() + ':' + $('#brick').val();
		var attr_list = '';
		$('#attributes select').each(function(k,v){
			attr_list += v.id + ':' + $(v).val() + ';';
		});
		$.ajax({
			url: '/products/'+pk+'/setcat',
			type: 'post',
			dataType: 'json',
			data:{
				cat:	category,
				avlst: attr_list
			},
			beforeSend: function(xhr){
				$('<img>', {
					src:'/static/site/img/spinner.gif',
					width: 20
					}).addClass('spinner')
					.appendTo('legend')
			},
			success: function(msg) {
				$('.spinner').remove();
				if (msg.status==1){var m='success';var al_txt='Product has been updated'}
				else{var m='error';var al_txt='Product has not been updated'}
				$('<div>').addClass('alert alert-'+m)
					.html(al_txt)
					.prepend(
						$('<button>', {'data-dismiss': 'alert'})
							.addClass('close').html('&times;')
					).prependTo('.tabbable');
				check_status(pk);
			},
			error: function(jqXHR, textStatus, errorThrown){
				$('.spinner').remove()
			}
		});
	}else{
		$(e).text('Save');
		$('#category :disabled,#attributes :disabled').removeAttr('disabled');
	}
}
function toggleMktEdit(e, pk){
	if ($(e).text() == "Save"){
		$(e).text('Edit');
		$('#market select').attr('disabled', 'disabled');
		/*$.ajax({
			url: '/products/'+pk+'/setmkt/',
			datatype: 'json',
			data:{
				mkt:	$('#tgt_mkt').val()
			},
			beforeSend: function(xhr){
				$('<img>', {
					src:'/static/site/img/spinner.gif',
					width: 20
					}).addClass('spinner')
					.appendTo('legend')
			},
			success: function(msg) {
				$('.spinner').remove()
				if (msg.status){m='success';al_txt='Product has been updated'}
				else{m='error';al_txt='Product has not been updated'}
				$('<div>').addClass('alert alert-'+m)
					.html(al_txt)
					.prepend(
						$('<button>', {'data-dismiss': 'alert'})
							.addClass('close').html('&times;')
					).prependTo('.tabbable')
				check_status(pk);
			},
			error: function(jqXHR, textStatus, errorThrown){
				$('.spinner').remove()
			}
		});*/
	}else{
		$(e).text('Save');
		$('#market :disabled').removeAttr('disabled');
	}
}
function fill_parents(pairs){
	var ps=pairs.split(';');
	$(ps).each(function(i,v){
		if (v!=''){
			v = v.split(':');
			if(v[0]=='S'){
				$('#segment option[value="'+v[1]+'"]').attr('selected','selected')
			}else if(v[0]=='F'){
				$('#family').empty().append(
					$('<option>',{value:v[1]}).text(v[2])
						.attr('selected','selected'),
					$('<option>', {value:''}).text('-----'))
			}else if(v[0]=='C'){
				$('#classes').empty().append(
					$('<option>',{value:v[1]}).text(v[2])
						.attr('selected','selected'),
					$('<option>', {value:''}).text('-----'))
			}else if(v[0]=='B'){
				$('#brick').empty().append(
					$('<option>',{value:v[1]}).text(v[2])
						.attr('selected','selected'),
					$('<option>', {value:''}).text('-----'))
					.trigger('change')
			}
		}
	})
}
function pollute_tree(res){
	$('#result-container').empty()
		.html(res)
}
function search_ajax(){
	$.ajax({
		url: '/products/searchcat',
		data:{
			key:$('input[name="catkey"]').val(),
			opt:$('input[name="brick_attr"]').val(),
			ext:$('input[name="exact"]').val()
		},
		beforeSend:function(){
			$('<img>', {
				src:'/static/site/img/spinner.gif',
				width: 20
				}).addClass('spinner')
				.appendTo($('input[value="submit"]').parent())
		},
		error: function(jqXHR, status, err) {},
		success: function(res){pollute_tree(res)}
	});
}
function chng_actv_nav(e){
	$(e).parent().siblings().removeClass('active');
	$(e).parent().addClass('active');
}
function go_tab(t){$('a[href="#'+ t +'"]').trigger('click')}
//function auto_fill(){
//	if( $('#auto-fill').is(':checked') ){
//		var desc = $('#id_brand').val() + ' ' 
//			+ $('#id_functional_name').val() + ' ' 
//			+ $('#id_net_content').val() + ' ' 
//			+ $('#id_net_content_uom').text() + ' ' 
//			+ $('#id_variant').val() + ' ' 
//		$('#id_product_description').val(desc);
//	}
//}

$(document).ready(function(){
	var search_wide=true;
	$('a[href="#detail"]').on('click', function(){chng_actv_nav($('.nav-list>li>a')[0])});
	$('a[href="#category"]').on('click', function(){chng_actv_nav($('.nav-list>li>a')[1])});
	$('a[href="#market"]').on('click', function(){chng_actv_nav($('.nav-list>li>a')[2])});
//	$('#id_brand,#id_functional_name, #id_variant, #auto-fill').change(function(e){auto_fill()});
	
	$("input[name='catkey']").keyup(function(e){
		if(e.keyCode == 13){search_ajax()}
	});
	$('#search_title').live('click', function(){
		$('#result-container div:not(#search_title)').toggle('slow');
		if (search_wide){ search_wide=false;
			$('#result-container b img').attr('src', '/static/site/img/expand.gif')
		}else{ search_wide=true;
			$('#result-container b img').attr('src', '/static/site/img/collapse.gif')
		}
	})
	$('#segment').live('change', function(){
		if (!$(this).val()){
			$('#family,#classes,#brick,#attributes').empty()
		}else{
		$.ajax({
			url:'/products/gettree',
			dataType:'json',
			data:{code:$(this).val()},
			error:function( jqXHR, status, err){$('.spinner').remove()},
			beforeSend:function(){
				$('<img>', {
					src:'/static/site/img/spinner.gif',
					width: 20
					}).addClass('spinner')
					.appendTo($('#family').parent())
			},
			success:function(res){
				$('.spinner').remove();
				$('#family,#classes,#brick,#attributes').empty()
					.append($('<option>', {value:''}).text('-----'));
				pollute_tree(res.result)
				if (res.children.length){
					$(res.children).each(function(k, v){
						$('#family').append(
							$('<option>', {value: v[0]}).text(v[1])
					)})
				}else{
					var attr_title = $('#attributes').siblings('legend')[1]
					$(attr_title).text('Attributes: (N/A)')
				}
			}
		})}
	});
	$('#family').live('change', function(){
		if (!$(this).val()){
			$('#classes,#brick,#attributes').empty()
		}else{
		$.ajax({
			url:'/products/gettree',
			dataType:'json',
			data:{code:$(this).val()},
			error:function( jqXHR, status, err){$('.spinner').remove()},
			beforeSend:function(){
				$('<img>', {
					src:'/static/site/img/spinner.gif',
					width: 20
					}).addClass('spinner')
					.appendTo($('#classes').parent())
			},
			success:function(res){
				$('.spinner').remove()
				$('#classes,#brick,#attributes').empty()
					.append($('<option>', {value:''}).text('-----'));
				pollute_tree(res.result)
				if (res.children.length){
					$(res.children).each(function(k, v){
						$('#classes').append(
							$('<option>', {value: v[0]}).text(v[1])
					)})
				}else{
					var attr_title = $('#attributes').siblings('legend')[1];
					$(attr_title).text('Attributes: (N/A)')
				}
			}
		})}
	});
	$('#classes').live('change', function(){
		if (!$(this).val()){
			$('#brick,#attributes').empty()
		}else{
		$.ajax({
			url:'/products/gettree',
			dataType:'json',
			data:{code:$(this).val()},
			error:function( jqXHR, status, err){$('.spinner').remove()},
			beforeSend:function(){
				$('<img>', {
					src:'/static/site/img/spinner.gif',
					width: 20
					}).addClass('spinner')
					.appendTo($('#brick').parent())
			},
			success:function(res){
				$('.spinner').remove()
				$('#brick,#attributes').empty()
					.append($('<option>', {value:''}).text('-----'));
				pollute_tree(res.result)
				if (res.children.length){
					$('#brick,#attributes').empty()
					$('#brick').append($('<option>', {value:''}).text('-----'));
					$(res.children).each(function(k, v){
						$('#brick').append(
							$('<option>', {value: v[0]}).text(v[1])
					)})
				}else{
					var attr_title = $('#attributes').siblings('legend')[1];
					$(attr_title).text('Attributes: (N/A)')
				}
			}
		})}
	});
	$('#brick').live('change', function(){
		if (!$(this).val()){
			$('#attributes').empty();
			var attr_title = $('#attributes').siblings('legend')[1];
			$(attr_title).text('Attributes: (N/A)')
		}else{
		$.ajax({
			url:'/products/gettree',
			dataType:'json',
			data:{code:$(this).val(), av:1},
			error:function( jqXHR, status, err){$('.spinner').remove()},
			beforeSend:function(){
				$('<img>', {
					src:'/static/site/img/spinner.gif',
					width: 20
					}).addClass('spinner')
					.appendTo('attributes')
			},
			success:function(res){
				$('.spinner').remove();
				$('#attributes').empty();
				if (res.children.length){
					attr_title = $('#attributes').siblings('legend')[1];
					$(attr_title).text('Attributes:');
					$(res.children).each(function(k, v){
						$('#attributes').append(
							$('<div>').addClass('row').append(
								$('<div>').addClass('col-xs-4').append(v[1]),
								$('<div>').addClass('col-xs-8').append(
									$('<select>', {id: v[0]}).addClass('form-control col-xs-12')
										.append($('<option>', {value:''}).text('-----')))
						))
						$(res.values[v[0]]).each(function(i, val){
							$('<option>', {value: val[0]}).text(val[1]).appendTo('#'+v[0])
						})
					})
				}else{
					var attr_title = $('#attributes').siblings('legend')[1];
					$(attr_title).text('Attributes: (N/A)');
					$('#attributes').append(
						$('<select>', {id: 'NA'}).append($('<option>')).hide()
					)
				}
			}
		})}
	});
	$('#tgt_mkt,#id_target_market').live('change', function(){
		code = $(this).val().toLowerCase();
		no_img = ['', 'ad', 'aq', 'bq', 'bl', 'cw', 'gg', 'im', 'je', 'mf', 'ss', 'sx'];
		if (no_img.indexOf(code) == -1){
			img_src = '/static/site/img/flags/gif/' + code +'.gif';
		}else{
			img_src = '';
		}
		if ($(this).parent().siblings().find('img').length == 0)
			$(this).parent().siblings().append($('<img>').attr('src', img_src));
		else $(this).parent().siblings().find('img').attr('src', img_src);
	});
});
