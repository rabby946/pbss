document.addEventListener('DOMContentLoaded', () => {
            const menuButton = document.getElementById('mobile-menu-button');
            const navMenu = document.getElementById('mobile-nav-menu');
            const closeButton = document.getElementById('drawer-close-button');
            const overlay = document.getElementById('drawer-overlay');
            const body = document.body;

            let touchStartX = 0;
            const swipeThreshold = 50; 

            const openMenu = () => {
                navMenu.classList.add('is-open');
                overlay.classList.remove('hidden');
                // Ensure overlay transition starts smoothly
                setTimeout(() => overlay.classList.add('opacity-50'), 10);
                body.classList.add('overflow-hidden');
            };

            const closeMenu = () => {
                navMenu.classList.remove('is-open');
                overlay.classList.remove('opacity-50');
                body.classList.remove('overflow-hidden');
                // Use a short delay before hiding the overlay to allow transition to finish
                setTimeout(() => {
                    overlay.classList.add('hidden');
                    // Reset transform to default for the next open animation
                    navMenu.style.transform = ''; 
                }, 400); 
            };

            // Event listeners for open/close buttons
            menuButton.addEventListener('click', openMenu);
            closeButton.addEventListener('click', closeMenu);
            overlay.addEventListener('click', closeMenu);

            // Close on any menu item click
            navMenu.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', closeMenu);
            });

            // --- Swipe Gesture Logic ---
            navMenu.addEventListener('touchstart', (e) => {
                touchStartX = e.touches[0].clientX;
                navMenu.classList.add('is-swiping');
            });

            navMenu.addEventListener('touchmove', (e) => {
                if (!navMenu.classList.contains('is-open')) return;
                
                const touchCurrentX = e.touches[0].clientX;
                const distance = touchCurrentX - touchStartX;
                const menuWidth = navMenu.offsetWidth;

                // Handle swipes to the right (closing the drawer)
                if (distance > 0) {
                    e.preventDefault(); 
                    
                    // The drawer is fully open (translateX(0)). We move it right (positive distance).
                    const newTransform = distance; 
                    navMenu.style.transform = `translateX(${newTransform}px)`;
                    
                    // Dim the overlay as the drawer slides away (0.5 max opacity -> 0 min opacity)
                    const opacity = 0.5 - (distance / menuWidth) * 0.5;
                    overlay.style.opacity = Math.max(0, opacity);
                }
            });

            navMenu.addEventListener('touchend', (e) => {
                navMenu.classList.remove('is-swiping');
                navMenu.style.transition = ''; 
                overlay.style.transition = ''; 

                const touchEndX = e.changedTouches[0].clientX;
                const swipeDistance = touchEndX - touchStartX;

                if (swipeDistance > swipeThreshold) {
                    // Swipe successful, close the menu
                    closeMenu();
                } else if (navMenu.classList.contains('is-open')) {
                    // Swipe unsuccessful, snap back to open position
                    navMenu.style.transform = `translateX(0)`;
                    overlay.style.opacity = '0.5';
                }
            });
        });

        // --- 2. Toast Notification Logic (Flash Messages) ---
        document.addEventListener('DOMContentLoaded', () => {
            const toastContainer = document.getElementById('toast-container');
            const toasts = Array.from(toastContainer.querySelectorAll('.toast-notification'));

            toasts.forEach(toast => {
                const isError = toast.dataset.isError === 'true';
                const timeout = parseInt(toast.dataset.timeout || '5000', 10);
                const message = toast.dataset.message;
                const title = toast.dataset.title;
                const iconClass = toast.dataset.icon;
                
                // Set colors based on type
                const bgColor = isError ? 'bg-red-50' : 'bg-green-50';
                const borderColor = isError ? 'border-red-500' : 'border-green-500';
                const iconColor = isError ? 'text-red-500' : 'text-green-500';
                const progressColor = isError ? 'bg-red-500' : 'bg-green-500';
                
                // Build internal HTML structure
                toast.classList.add(bgColor, borderColor, 'border-l-4', 'shadow-xl');
                toast.innerHTML = `
                    <div class="flex-shrink-0 ${iconColor} text-xl mr-3">
                        <i class="fas ${iconClass}"></i>
                    </div>
                    <div class="flex-grow">
                        <p class="text-sm font-semibold text-gray-900">${title}</p>
                        <p class="text-sm text-gray-600 mt-0.5">${message}</p>
                    </div>
                    <button class="flex-shrink-0 text-gray-400 hover:text-gray-700 ml-4 transition text-xl leading-none close-toast" aria-label="Close">&times;</button>
                    <div class="absolute bottom-0 left-0 h-1 ${progressColor} w-full toast-notification__progress"></div>
                `;

                // Show the toast with animation
                setTimeout(() => {
                    toast.classList.add('show');
                }, 50); 

                // Dismiss function
                const dismissToast = () => {
                    toast.style.animation = 'none'; 
                    toast.style.transform = 'translateX(110%)'; 
                    toast.style.opacity = '0';
                    setTimeout(() => toast.remove(), 400); 
                };

                // Auto-dismiss timer
                const autoDismissTimer = setTimeout(dismissToast, timeout);

                // Close button listener
                toast.querySelector('.close-toast').addEventListener('click', () => {
                    clearTimeout(autoDismissTimer);
                    dismissToast();
                });
            });
        });
        tsParticles.load({
            id: "tsparticles",
            options: {
                fullScreen: {
                    enable: false, // We use the custom .particles-bg div
                },
                background: {
                    color: {
                        value: "transparent", // Let CSS handle the background color
                    },
                },
                fpsLimit: 60,
                interactivity: {
                    events: {
                        onHover: {
                            enable: true,
                            mode: "repulse", // Particles gently move away from the cursor
                        },
                        resize: true,
                    },
                    modes: {
                        repulse: {
                            distance: 100,
                            duration: 0.4,
                        },
                    },
                },
                particles: {
                    number: {
                        value: 50, // Subtle quantity
                        density: {
                            enable: true,
                            value_area: 800,
                        },
                    },
                    color: {
                        value: "#adb5bd", // Soft, professional gray/blue color
                    },
                    shape: {
                        type: "circle",
                    },
                    opacity: {
                        value: 0.5,
                        random: true,
                    },
                    size: {
                        value: 3, // Small size
                        random: true,
                    },
                    line_linked: {
                        enable: true, // Lines connecting the dots
                        distance: 150,
                        color: "#adb5bd",
                        opacity: 0.4,
                        width: 1,
                    },
                    move: {
                        enable: true,
                        speed: 1, // Slow, gentle movement
                        direction: "none",
                        random: false,
                        straight: false,
                        out_mode: "out",
                        bounce: false,
                    },
                },
                detectRetina: true,
            },
        });