function render_results(data, inputtext) {
	// alert('inputtext ' + inputtext);
	// alert("display results response " + JSON.stringify(data, null, 2));

	var rblock = document.getElementById("searchresults");
	docs = data["response"]["docs"];
	arr = [];

	for (i = 0; i < docs.length; i++) {
		temp_arr = docs[i]["id"].split("/")
		temp_str = temp_arr[temp_arr.length - 1]
		doc_name = temp_str.split(".")[0]

		if (doc_name.startsWith("en")) {
			continue;
		}

		var searchresult = document.createElement('p');

    	summ_url = "http://localhost:8080?name=" + doc_name + '&api=aylien';
    	$.ajax({
	    	type:     "GET",
	    	url:      summ_url,
	    	success: function(data) {
	    		json_data = JSON.parse(data);
	    		doc_name = json_data.doc;
	    		summ = json_data.summary;

	    		var summary = document.createElement('p');
	    		summary.innerHTML = summ;
	    		
	    		var titlelink = document.createElement('a');
	    		titlelink.target = "_blank";
				titlelink.style.fontSize = "x-large";
    			titlelink.textContent = doc_name.split('_').join(' ') ;
    			titlelink.href = "display.html?page=" + doc_name;
    			
    			searchresult.appendChild(titlelink);
	    		searchresult.appendChild(summary);
	    	}
	    });
		rblock.appendChild(searchresult);
	}

	entity_search_url = "http://localhost:8080?name=" + inputtext + '&api=google' + '&limit=1';
	// alert(entity_search_url);
	$.ajax({
	    type:     "GET",
	    url:      entity_search_url,
	    success: function(data) {
	    	// alert('google limit=1 ' + JSON.stringify(data, null, 2));
			json_data = JSON.parse(data);
			var entity_data = document.createElement('p');

			var hh2 = document.createElement('h2');
			if (json_data.itemListElement[0] == null) {
				return;
			}
			hh2.innerHTML = json_data.itemListElement[0].result.name;
			document.getElementById("entity").appendChild(hh2);

			if (json_data.itemListElement[0].result.image != null) {
				var img = document.createElement('img');
				img.src = json_data.itemListElement[0].result.image.contentUrl;
				document.getElementById("entity").appendChild(img);
			}

			entity_data.innerHTML = json_data.itemListElement[0].result.detailedDescription.articleBody;
			document.getElementById("entity").appendChild(entity_data);
	    }
	});

	
	limit = 10;
	entity_search_url = "http://localhost:8080?name=" + inputtext + '&api=google' + '&limit=' + limit.toString();
	// alert(entity_search_url);
	$.ajax({
	    type:     "GET",
	    url:      entity_search_url,
	    success: function(data) {
	    	// alert('google limit=10 ' + JSON.stringify(data, null, 2));
			json_data = JSON.parse(data);
			var r_searches = document.getElementById('menu');
			for (i = 0; i < json_data.itemListElement.length; i++) {
				related_name = json_data.itemListElement[i].result.name;
				if (json_data.itemListElement[i].result.description != null) {
					related_name += '-' + json_data.itemListElement[i].result.description;
				}
				related_url = json_data.itemListElement[i].result.url;
				r_searches.innerHTML += '<li> <a target="_blank" href="' + related_url + '">' + related_name + '</a></li>';

			}
	    }
	});


	$('#searchlist').show();
}


function re_search(suggested_word) {
	document.getElementById("inputtext").value = suggested_word.split('_').join(' ');
	displayresults(suggested_word);
}

function spell_check(data) {
	// alert("Spell checker response " + JSON.stringify(data, null, 2));

	if (data["spellcheck"]["suggestions"] == null || data["spellcheck"]["suggestions"][1] == null ) {
			return;
	}
	suggestion_list = data["spellcheck"]["suggestions"][1]["suggestion"];
	max_freq = 0;
	suggested_word = "";
	for (i = 0; i < suggestion_list.length; i++) {
		freq = parseInt(suggestion_list[i]["freq"]);
		if (freq > max_freq) {
			max_freq = freq;
			suggested_word = suggestion_list[i]["word"];
		}
	}
	var spellcheck = document.getElementById("spellcheck");
	spellcheck.innerHTML = "<h2>Did you mean: <a onclick=re_search('"  + suggested_word + "'); href='javascript:void(0)'>" + suggested_word.split('_').join(' ') + "</a></h2>";
	// alert(spellcheck.innerHTML);
	$("#spell").show();
}


function displayresults(inputtext) {
	$("#searchresults").empty();
	$("#menu").empty();
	$("#entity").empty();
	$("#spellcheck").empty();

	spell_check_url = "http://localhost:8983/solr/tempinfoproject/spell?spellcheck=true&wt=json&rows=5&json.wrf=callback&indent=true&q=" + inputtext;
	// alert(spell_check_url);

	$.ajax({
        type: 'GET',
        async: false,
        url: spell_check_url,
        dataType: 'JSONP',
        jsonpCallback: 'callback',
        crossDomain: true,
        success : function(data) {
        	spell_check(data);
        	render_results(data, inputtext);
        }
	});


	// url = "http://localhost:8983/solr/inforetrievalproject/select?defType=dismax&rows=5&wt=json&json.wrf=JSON.parse&indent=true&q=" + inputtext;
	// alert(url);

	// $.ajax({
 //        type: 'GET',
 //        url: url,
 //        dataType: 'JSONP',
 //        crossDomain: true,
 //        success : function(data){
 //        	data = JSON.parse(data);
 //        	render_results(data, inputtext);
 //        }
	// });
}