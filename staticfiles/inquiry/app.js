document.addEventListener('DOMContentLoaded', function(){
  const categorySelect = document.getElementById('category-select');
  const productsList = document.getElementById('products-list');
  const cartItemsDiv = document.getElementById('cart-items');
  const cartCountBadge = document.getElementById('cart-count');

  const cart = [];
  const fallbackImage = 'https://images.pexels.com/photos/3962287/pexels-photo-3962287.jpeg?w=640';

  function findInCart(id){ return cart.find(i => i.id === id); }

  function updateCartCount(){
    cartCountBadge.textContent = cart.length;
  }

  function makeProductNode(p){
    const wrap = document.createElement('div');
    wrap.className = 'product-card';

    // Image - ensure it loads with error handling
    const img = document.createElement('img');
    img.src = p.image_url && p.image_url.trim() !== '' ? p.image_url : fallbackImage;
    img.alt = p.name;
    img.loading = 'lazy';
    img.onerror = function(){ this.src = fallbackImage; };
    wrap.appendChild(img);

    const meta = document.createElement('div');
    meta.className = 'meta';
    const h = document.createElement('h4');
    h.textContent = p.name;
    meta.appendChild(h);
    wrap.appendChild(meta);

    const controls = document.createElement('div');
    controls.className = 'controls';
    const addBtn = document.createElement('button');
    addBtn.type = 'button';
    addBtn.className = 'add-btn';
    addBtn.textContent = 'Add';

    addBtn.addEventListener('click', function(e){
      e.preventDefault();
      const existing = findInCart(p.id);
      if(existing){
        const idx = cart.indexOf(existing);
        if(idx > -1) cart.splice(idx, 1);
        addBtn.classList.remove('added');
        addBtn.textContent = 'Add';
      } else {
        cart.push({id: p.id, name: p.name, image_url: p.image_url, qty: 1});
        addBtn.classList.add('added');
        addBtn.textContent = 'Added';
      }
      renderCart();
      updateCartCount();
    });

    controls.appendChild(addBtn);
    wrap.appendChild(controls);
    return wrap;
  }

  function renderCart(){
    cartItemsDiv.innerHTML = '';
    if(cart.length === 0){
      cartItemsDiv.textContent = 'No items selected yet.';
      return;
    }

    cart.forEach((item, idx) => {
      const div = document.createElement('div');
      div.className = 'cart-item';

      const img = document.createElement('img');
      img.src = item.image_url && item.image_url.trim() !== '' ? item.image_url : fallbackImage;
      img.alt = item.name;
      img.loading = 'lazy';
      img.onerror = function(){ this.src = fallbackImage; };
      div.appendChild(img);

      const name = document.createElement('div');
      name.className = 'name';
      name.textContent = item.name;
      div.appendChild(name);

      // Hidden product_id
      const hidden = document.createElement('input');
      hidden.type = 'hidden';
      hidden.name = 'product_id';
      hidden.value = item.id;
      div.appendChild(hidden);

      const qty = document.createElement('input');
      qty.type = 'number';
      qty.name = 'quantity';
      qty.className = 'qty';
      qty.min = 1;
      qty.max = 999;
      qty.value = item.qty || 1;
      qty.addEventListener('change', function(){
        const v = parseInt(this.value) || 0;
        item.qty = Math.max(1, v);
        if(v <= 0){
          const idx = cart.indexOf(item);
          if(idx > -1) cart.splice(idx, 1);
        }
        renderCart();
        updateCartCount();
      });
      div.appendChild(qty);

      const removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.className = 'remove';
      removeBtn.textContent = 'Remove';
      removeBtn.addEventListener('click', function(e){
        e.preventDefault();
        const idx = cart.indexOf(item);
        if(idx > -1) cart.splice(idx, 1);
        renderCart();
        updateCartCount();
        // Re-render products to reset Add buttons
        loadProductsByCategory(categorySelect.value);
      });
      div.appendChild(removeBtn);

      cartItemsDiv.appendChild(div);
    });
  }

  function loadProductsByCategory(catId){
    productsList.innerHTML = '<p class="empty-state">Loading products...</p>';
    if(!catId) {
      productsList.innerHTML = '<p class="empty-state">Select a category to view products</p>';
      return;
    }
    
    fetch(`/api/products/?category_id=${catId}`)
      .then(r => r.json())
      .then(data => {
        productsList.innerHTML = '';
        if(!data.products || data.products.length === 0){
          productsList.innerHTML = '<p class="empty-state">No products in this category</p>';
          return;
        }
        (data.products || []).forEach(p => {
          const cardNode = makeProductNode(p);
          // Mark as added if in cart
          if(findInCart(p.id)){
            cardNode.querySelector('.add-btn').classList.add('added');
            cardNode.querySelector('.add-btn').textContent = 'Added';
          }
          productsList.appendChild(cardNode);
        });
      })
      .catch(err => {
        console.error('Error loading products:', err);
        productsList.innerHTML = '<p class="empty-state">Error loading products. Please try again.</p>';
      });
  }

  categorySelect && categorySelect.addEventListener('change', function(){
    loadProductsByCategory(this.value);
  });

  updateCartCount();
});
