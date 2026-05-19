// GED Universitaire — Main JS

document.addEventListener('DOMContentLoaded', function () {

  // Sidebar toggle (mobile)
  const hamburger = document.querySelector('.hamburger');
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.getElementById('sidebar-overlay');

  if (hamburger && sidebar) {
    hamburger.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      overlay && overlay.classList.toggle('show');
    });
  }
  if (overlay) {
    overlay.addEventListener('click', () => {
      sidebar && sidebar.classList.remove('open');
      overlay.classList.remove('show');
    });
  }

  // Auto-dismiss alerts after 4s
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity .4s';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 400);
    }, 4000);
  });

  // Upload drag & drop
  const uploadZone = document.getElementById('upload-zone');
  const fileInput = document.getElementById('id_fichier');

  if (uploadZone && fileInput) {
    uploadZone.addEventListener('click', () => fileInput.click());
    uploadZone.addEventListener('dragover', e => {
      e.preventDefault();
      uploadZone.classList.add('dragover');
    });
    uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
    uploadZone.addEventListener('drop', e => {
      e.preventDefault();
      uploadZone.classList.remove('dragover');
      const file = e.dataTransfer.files[0];
      if (file) {
        const dt = new DataTransfer();
        dt.items.add(file);
        fileInput.files = dt.files;
        updateUploadZone(file);
      }
    });
    fileInput.addEventListener('change', () => {
      if (fileInput.files[0]) updateUploadZone(fileInput.files[0]);
    });
  }

  function updateUploadZone(file) {
    const zone = document.getElementById('upload-zone');
    if (!zone) return;
    zone.innerHTML = `
      <div class="upload-icon"><i class="bi bi-file-earmark-check text-success"></i></div>
      <p class="upload-text text-success">${file.name}</p>
      <p class="upload-sub">${(file.size / 1024).toFixed(1)} KB — Cliquer pour changer</p>
    `;
  }

  // Progress bar upload simulation
  const uploadForm = document.getElementById('upload-form');
  if (uploadForm) {
    uploadForm.addEventListener('submit', function () {
      const bar = document.getElementById('upload-progress');
      if (!bar) return;
      bar.parentElement.classList.remove('d-none');
      let width = 0;
      const interval = setInterval(() => {
        width = Math.min(width + Math.random() * 15, 90);
        bar.style.width = width + '%';
        if (width >= 90) clearInterval(interval);
      }, 200);
    });
  }

  // Active sidebar link
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  // Tooltips Bootstrap
  const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipEls.forEach(el => new bootstrap.Tooltip(el));

  // Table row click to navigate
  document.querySelectorAll('tr[data-href]').forEach(row => {
    row.style.cursor = 'pointer';
    row.addEventListener('click', () => {
      window.location.href = row.dataset.href;
    });
  });

  // Confirmation dialogs
  document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', function (e) {
      if (!confirm(this.dataset.confirm)) e.preventDefault();
    });
  });

  // Search input with debounce
  const searchInputs = document.querySelectorAll('.live-search');
  searchInputs.forEach(input => {
    let timeout;
    input.addEventListener('input', function () {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        const form = this.closest('form');
        if (form) form.submit();
      }, 600);
    });
  });

});
