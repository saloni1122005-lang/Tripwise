#!/usr/bin/env python3
"""Patch explorer.html: inject Explore Destination JS block."""

path = r'c:\Users\Saloni\project\templates\explorer.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

JS_BLOCK = """

/* =========================================================
   EXPLORE DESTINATION - 3-Tab (Attractions / Hotels / Restaurants)
   ========================================================= */
(function() {
  if (!currentDest) return;

  var exploreTab = 'attractions';

  function showExploreSkeletons() {
    var grid = document.getElementById('exploreDestGrid');
    if (!grid) return;
    var html = '';
    for (var i = 0; i < 6; i++) {
      html += '<div class="col-md-6 col-xl-4"><div class="card h-100 border-0 shadow-sm rounded-4 overflow-hidden" style="min-height:370px;"><div class="skeleton-card" style="height:200px;width:100%;"></div><div class="card-body p-3"><div class="skeleton-card mb-2" style="height:20px;width:65%;border-radius:4px;"></div><div class="skeleton-card mb-2" style="height:14px;width:40%;border-radius:4px;"></div><div class="skeleton-card mb-2" style="height:13px;width:90%;border-radius:4px;"></div><div class="skeleton-card mb-3" style="height:13px;width:75%;border-radius:4px;"></div><div class="d-flex gap-2 mt-3"><div class="skeleton-card" style="height:32px;width:80px;border-radius:20px;"></div><div class="skeleton-card" style="height:32px;width:130px;border-radius:20px;"></div></div></div></div></div>';
    }
    grid.innerHTML = html;
  }

  function buildStars(rating) {
    if (rating == null) return '<span class="text-muted small">No rating</span>';
    var full  = Math.floor(rating);
    var half  = (rating - full) >= 0.5 ? 1 : 0;
    var empty = 5 - full - half;
    var s = '';
    for (var i = 0; i < full;  i++) s += '<i class="fa-solid fa-star text-warning" style="font-size:.8rem;"></i>';
    if (half)                        s += '<i class="fa-solid fa-star-half-stroke text-warning" style="font-size:.8rem;"></i>';
    for (var i2 = 0; i2 < empty; i2++) s += '<i class="fa-regular fa-star text-warning" style="font-size:.8rem;"></i>';
    s += '<span class="ms-1 fw-bold" style="font-size:.85rem;">' + parseFloat(rating).toFixed(1) + '</span>';
    return s;
  }

  var FALLBACKS = {
    attractions: 'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=600&auto=format&fit=crop',
    hotels:      'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=600&auto=format&fit=crop',
    restaurants: 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&auto=format&fit=crop'
  };

  function renderExplorePlaces(places) {
    var grid = document.getElementById('exploreDestGrid');
    if (!grid) return;
    if (!places || places.length === 0) {
      grid.innerHTML = '<div class="col-12 text-center py-5"><i class="fa-solid fa-magnifying-glass fa-3x text-muted mb-3"></i><h5 class="fw-bold">No results found for this destination.</h5><p class="text-muted">Try a different destination or switch tabs.</p></div>';
      return;
    }
    var fallback = FALLBACKS[exploreTab] || FALLBACKS.attractions;
    var html = '';
    places.forEach(function(place) {
      var isFav   = favoritePlaces.includes(place.place_id) || favoritePlaces.includes(String(place.place_id));
      var favIcon = isFav ? 'fa-solid fa-heart text-danger' : 'fa-regular fa-heart text-white';
      var photo   = place.photo_url || fallback;
      var stars   = buildStars(place.rating);
      var reviews = place.reviews ? '<span class="text-muted" style="font-size:.78rem;">(' + Number(place.reviews).toLocaleString() + ' reviews)</span>' : '';
      var openBadge = '';
      if (place.open_now === true)
        openBadge = '<span class="badge bg-success bg-opacity-15 text-success rounded-pill px-2" style="font-size:.7rem;"><i class="fa-solid fa-circle me-1" style="font-size:.4rem;vertical-align:middle;"></i>Open Now</span>';
      else if (place.open_now === false)
        openBadge = '<span class="badge bg-danger bg-opacity-15 text-danger rounded-pill px-2" style="font-size:.7rem;"><i class="fa-solid fa-circle me-1" style="font-size:.4rem;vertical-align:middle;"></i>Closed</span>';
      var safeName  = (place.name     || '').replace(/"/g, '&quot;');
      var safeAddr  = (place.address  || '').replace(/"/g, '&quot;');
      var safeMaps  = (place.maps_url || '#').replace(/"/g, '&quot;');
      var safePid   = (place.place_id || '').replace(/"/g, '&quot;');
      var safePhoto = photo.replace(/"/g, '&quot;');
      var openSt    = place.open_now === true ? 'Open Now' : place.open_now === false ? 'Closed' : '';
      html += '<div class="col-md-6 col-xl-4">' +
        '<article class="card h-100 border-0 shadow-sm rounded-4 overflow-hidden explore-dest-card" style="transition:transform .22s ease,box-shadow .22s ease;">' +
        '<div class="position-relative" style="height:200px;overflow:hidden;">' +
        '<img src="' + photo + '" loading="lazy" onerror="this.src=\\'' + fallback + '\\'" class="w-100 h-100 object-fit-cover" style="transition:transform .35s ease;" alt="' + safeName + '">' +
        '<button type="button" class="btn btn-sm rounded-circle position-absolute d-flex align-items-center justify-content-center" style="top:10px;right:10px;width:36px;height:36px;background:rgba(0,0,0,.45);border:none;backdrop-filter:blur(4px);z-index:2;" data-place-id="' + safePid + '" onclick="toggleExploreFav(this)" title="Save to favorites"><i class="' + favIcon + '" style="font-size:.9rem;pointer-events:none;"></i></button>' +
        (openBadge ? '<div class="position-absolute" style="bottom:10px;left:10px;">' + openBadge + '</div>' : '') +
        '</div>' +
        '<div class="card-body d-flex flex-column p-3">' +
        '<h6 class="fw-bold mb-1" style="line-height:1.3;font-size:.97rem;">' + (place.name || 'Unknown Place') + '</h6>' +
        '<div class="d-flex align-items-center gap-2 mb-2 flex-wrap"><div class="d-flex align-items-center gap-1">' + stars + '</div>' + reviews + '</div>' +
        (place.address ? '<p class="text-muted small mb-3 flex-grow-1" style="line-height:1.4;font-size:.82rem;"><i class="fa-solid fa-location-dot me-1 text-primary"></i>' + place.address + '</p>' : '<div class="flex-grow-1"></div>') +
        '<div class="d-flex gap-2 flex-wrap mt-auto pt-2">' +
        '<a href="' + safeMaps + '" target="_blank" rel="noopener" class="btn btn-sm btn-outline-primary rounded-pill px-3 fw-semibold"><i class="fa-solid fa-map-location-dot me-1"></i>Maps</a>' +
        '<button type="button" class="btn btn-sm btn-primary rounded-pill px-3 fw-semibold"' +
        ' data-place-id="' + safePid + '" data-name="' + safeName + '" data-desc="' + safeAddr + '"' +
        ' data-best-time="" data-duration="" data-category="' + exploreTab + '"' +
        ' data-address="' + safeAddr + '" data-opening-status="' + openSt + '"' +
        ' data-maps-url="' + safeMaps + '" data-rating="' + (place.rating || '') + '"' +
        ' data-distance="" data-image-url="' + safePhoto + '"' +
        ' onclick="openTripPicker(this.dataset)"><i class="fa-solid fa-plus me-1"></i>Add to Itinerary</button>' +
        '</div></div></article></div>';
    });
    grid.innerHTML = html;
    grid.querySelectorAll('.explore-dest-card').forEach(function(card) {
      card.addEventListener('mouseenter', function() {
        card.style.transform = 'translateY(-4px)';
        card.style.boxShadow = '0 12px 32px rgba(0,0,0,.13)';
        var img = card.querySelector('img');
        if (img) img.style.transform = 'scale(1.05)';
      });
      card.addEventListener('mouseleave', function() {
        card.style.transform = '';
        card.style.boxShadow = '';
        var img = card.querySelector('img');
        if (img) img.style.transform = '';
      });
    });
  }

  function loadExploreDest() {
    showExploreSkeletons();
    fetch('/explore/api/explore-destination?dest=' + encodeURIComponent(currentDest) + '&tab=' + encodeURIComponent(exploreTab))
      .then(function(r) { return r.json(); })
      .then(function(data) { renderExplorePlaces(data); })
      .catch(function() {
        var g = document.getElementById('exploreDestGrid');
        if (g) g.innerHTML = '<div class="col-12 text-center py-5"><i class="fa-solid fa-triangle-exclamation fa-3x text-warning mb-3"></i><h5 class="fw-bold">Failed to load places.</h5><p class="text-muted">Check your connection and try again.</p></div>';
      });
  }

  document.querySelectorAll('.explore-tab-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      document.querySelectorAll('.explore-tab-btn').forEach(function(b) {
        b.style.background = 'transparent';
        b.style.color      = '#6b7280';
        b.style.border     = '1.5px solid #e5e7eb';
        b.classList.remove('active');
      });
      btn.style.background = 'linear-gradient(135deg,#6366f1,#8b5cf6)';
      btn.style.color      = '#fff';
      btn.style.border     = 'none';
      btn.classList.add('active');
      exploreTab = btn.dataset.tab;
      loadExploreDest();
    });
  });

  window.toggleExploreFav = function(btn) {
    var placeId = btn.dataset.placeId;
    if (!placeId) return;
    var icon = btn.querySelector('i');
    var fd = new FormData();
    fd.append('place_id', placeId);
    fetch('/explore/favorite', { method: 'POST', body: fd })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        icon.className = data.favorited ? 'fa-solid fa-heart text-danger' : 'fa-regular fa-heart text-white';
      });
  };

  loadExploreDest();
})();
"""

ANCHOR = '</script>\n{% endblock %}'

if ANCHOR in content:
    content = content.replace(ANCHOR, JS_BLOCK + '\n</script>\n{% endblock %}', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('SUCCESS: JS block injected. File now', len(content), 'bytes')
else:
    print('FAIL: anchor not found')
    idx = content.rfind('</script>')
    print('Last </script> at char index:', idx)
    print('Context:', repr(content[max(0,idx-80):idx+30]))
