document.addEventListener("DOMContentLoaded", function() {
    const generators = document.querySelectorAll('.cmd-gen');

    generators.forEach(gen => {
        const configs = JSON.parse(gen.getAttribute('data-configs'));
        const display = gen.querySelector('.cmd-gen-content');
        const rows = gen.querySelectorAll('.cmd-gen-row');

        function update() {
            const selected = Array.from(rows).map(row =>
                row.querySelector('.cmd-gen-btn.active').getAttribute('data-opt')
            ).join(',');

            display.innerText = configs[selected] || "This configuration is not supported.";
        }

        gen.addEventListener('click', e => {
            if (e.target.classList.contains('cmd-gen-btn')) {
                const row = e.target.closest('.cmd-gen-row');
                row.querySelectorAll('.cmd-gen-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                update();
            }
        });

        update();
    });
});
