document.addEventListener('DOMContentLoaded', () => {
    const stockInputs = document.querySelectorAll('#stock');
    stockInputs.forEach((input) => {
        input.addEventListener('input', () => {
            const value = parseInt(input.value, 10);
            const boxes = document.querySelectorAll('#size-container input[type="checkbox"]');
            boxes.forEach((box) => {
                box.disabled = value < 1;
            });
        });
    });

    const revenueStat =
        document.getElementById('revenueStat');

    const revenueModal =
        document.getElementById('revenueModal');

    const closeRevenueModal =
        document.getElementById('closeRevenueModal');

    const revenueTabs =
        document.querySelectorAll('.revenue-tab');

    const revenuePeriodLabel =
        document.getElementById('revenuePeriodLabel');

    const revenuePeriodAmount =
        document.getElementById('revenuePeriodAmount');


    // Stop if revenue elements don't exist
    if (
        !revenueStat ||
        !revenueModal ||
        !closeRevenueModal ||
        !revenuePeriodAmount
    ) {
        return;
    }


    // Revenue values from HTML

    const revenueData = {

        today: {
            label: 'Today',
            amount: revenuePeriodAmount.dataset.today
        },

        week: {
            label: 'This Week',
            amount: revenuePeriodAmount.dataset.week
        },

        month: {
            label: 'This Month',
            amount: revenuePeriodAmount.dataset.month
        }

    };


    // OPEN MODAL

    revenueStat.addEventListener('click', () => {

        revenueModal.style.display = 'flex';

    });


    // CLOSE MODAL

    closeRevenueModal.addEventListener('click', () => {

        revenueModal.style.display = 'none';

    });


    // CHANGE PERIOD

    revenueTabs.forEach((tab) => {

        tab.addEventListener('click', () => {

            revenueTabs.forEach((item) => {

                item.classList.remove('active');

            });


            tab.classList.add('active');


            const period =
                tab.dataset.period;

            const data =
                revenueData[period];


            revenuePeriodLabel.textContent =
                data.label;

            revenuePeriodAmount.textContent =
                `₹${data.amount}`;

        });

    });


    // CLOSE WHEN CLICKING OUTSIDE

    revenueModal.addEventListener('click', (event) => {

        if (event.target === revenueModal) {

            revenueModal.style.display =
                'none';

        }

    });


});


