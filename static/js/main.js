/**
 * VIVA - LIVE BETTER
 * Main JavaScript Controller
 */

document.addEventListener('DOMContentLoaded', function () {
  // Toast notification helper
  window.showVivaToast = function (message, type = 'success') {
    let container = document.getElementById('viva-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'viva-toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const bgClass = type === 'success' ? 'bg-dark text-white' : (type === 'warning' ? 'bg-warning text-dark' : 'bg-danger text-white');
    const icon = type === 'success' ? 'bi-check-circle-fill text-success' : (type === 'warning' ? 'bi-exclamation-triangle-fill' : 'bi-x-circle-fill');

    toast.className = `toast align-items-center ${bgClass} border-0 shadow-lg show mb-2`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center gap-2">
          <i class="bi ${icon} fs-5"></i>
          <span>${message}</span>
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 400);
    }, 3500);
  };

  // Add to Cart AJAX
  document.querySelectorAll('.ajax-add-to-cart').forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();
      const productId = this.getAttribute('data-product-id');
      const quantity = this.getAttribute('data-quantity') || 1;

      fetch('/add-to-cart', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: `product_id=${encodeURIComponent(productId)}&quantity=${encodeURIComponent(quantity)}`
      })
      .then(res => {
        if (res.redirected) {
          window.location.href = res.url;
          return null;
        }
        return res.json();
      })
      .then(data => {
        if (!data) return;
        if (data.status === 'success') {
          showVivaToast(data.message || 'Added to shopping cart!', 'success');
          // Update cart badge
          const badge = document.querySelector('.header-cart-badge');
          if (badge && data.cart_count !== undefined) {
            badge.textContent = data.cart_count;
            badge.style.display = data.cart_count > 0 ? 'flex' : 'none';
          }
        } else {
          showVivaToast(data.message || 'Could not add to cart.', 'warning');
        }
      })
      .catch(err => {
        console.error(err);
        window.location.href = '/cart';
      });
    });
  });

  // Add to Wishlist AJAX
  document.querySelectorAll('.ajax-add-to-wishlist').forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();
      const productId = this.getAttribute('data-product-id');
      const self = this;

      fetch('/add-to-wishlist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: `product_id=${encodeURIComponent(productId)}`
      })
      .then(res => {
        if (res.redirected) {
          window.location.href = res.url;
          return null;
        }
        return res.json();
      })
      .then(data => {
        if (!data) return;
        showVivaToast(data.message, data.status === 'success' ? 'success' : 'warning');
        if (data.status === 'success') {
          self.classList.add('active');
          const heartIcon = self.querySelector('i');
          if (heartIcon) {
            heartIcon.classList.remove('bi-heart');
            heartIcon.classList.add('bi-heart-fill');
          }
        }
        // Update wishlist badge
        const badge = document.querySelector('.header-wishlist-badge');
        if (badge && data.wishlist_count !== undefined) {
          badge.textContent = data.wishlist_count;
          badge.style.display = data.wishlist_count > 0 ? 'flex' : 'none';
        }
      })
      .catch(err => {
        console.error(err);
        window.location.href = '/wishlist';
      });
    });
  });

  // Quantity widget helper
  document.querySelectorAll('.quantity-widget').forEach(widget => {
    const decBtn = widget.querySelector('.quantity-dec');
    const incBtn = widget.querySelector('.quantity-inc');
    const input = widget.querySelector('.quantity-input');
    const maxStock = parseInt(input.getAttribute('max') || '99', 10);

    if (decBtn && incBtn && input) {
      decBtn.addEventListener('click', () => {
        let val = parseInt(input.value, 10) || 1;
        if (val > 1) {
          input.value = val - 1;
          input.dispatchEvent(new Event('change'));
        }
      });

      incBtn.addEventListener('click', () => {
        let val = parseInt(input.value, 10) || 1;
        if (val < maxStock) {
          input.value = val + 1;
          input.dispatchEvent(new Event('change'));
        } else {
          showVivaToast(`Max available stock is ${maxStock}`, 'warning');
        }
      });
    }
  });
});
