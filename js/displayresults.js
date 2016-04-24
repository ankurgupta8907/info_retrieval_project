function displayresults(inputtext) {
	url = "http://localhost:8983/solr/inforetrievalproject/select?defType=dismax&rows=5&wt=json&json.wrf=callback&indent=true&q=" + inputtext;

	$.ajax({
        type: 'GET',
        url: url,
        dataType: 'JSONP',
        jsonpCallback: 'callback',
        crossDomain: true
	}).done(function (data) {
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
		$.ajax({
		    type:     "GET",
		    url:      entity_search_url,
		    success: function(data) {
				json_data = JSON.parse(data);
				var entity_data = document.createElement('p');

				var hh2 = document.createElement('h2');
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
		$.ajax({
		    type:     "GET",
		    url:      entity_search_url,
		    success: function(data) {
				json_data = JSON.parse(data);
				var r_searches = document.getElementById('menu');
				for (i = 0; i < limit; i++) {
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
	});
}