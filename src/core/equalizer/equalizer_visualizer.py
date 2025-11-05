import numpy as np
import pygame
import math
import pygame.gfxdraw

from .audio_file_processor import AudioFileProcessor
from modules.console import Console

class EqualizerVisualizer:
    """
    A real-time audio visualizer that renders a dynamic, holographic, 
    JARVIS-style display using frequency spectrum data derived from audio files.
    
    It requires an AudioFileProcessor instance to supply frequency and peak data.
    """

    def __init__(self, caption: str, width: int = 1200, height: int = 700) -> None:
        """
        Initializes the visualizer, sets up pygame, the mixer, and loads resources.
        
        Args:
            caption (str): The title for the display window.
            width (int, optional): The width of the display window. Defaults to 1200.
            height (int, optional): The height of the display window. Defaults to 700.
        """
        pygame.init()
        
        # Initialize the mixer with standard settings for high-quality audio
        # 44100Hz frequency, -16 bit signed samples, 2 channels (stereo), 512 buffer size.
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(caption)

        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize the audio processing unit. Handles file loading, playback, and FFT.
        try:
            # Assumes AudioFileProcessor handles 32 frequency bands.
            self.audio_processor = AudioFileProcessor(num_bands=32)
        except Exception as e:
            Console.error("EqualizerVisualizer Error: Failed to initialize AudioProcessor. Exit.")
            pygame.quit()
            import sys
            sys.exit(1)

        # --- VISUAL TWEAKABLES ---
        # Constants defining the aesthetic and responsiveness of the visualization.
        
        # General
        self.FPS = 60                       # Target frames per second
        self.ROTATION_SPEED = 0.02          # Speed of the main visual rotation
        self.HUD_ROTATION_SPEED = 0.01      # Speed of the outer HUD elements

        # Bass Sensitivity
        self.BASS_RAY_MULTIPLIER: float      = 1     # Multiplier for bass ray length
        self.BASS_CORE_SENSITIVITY: int      = 75    # Strength of core size pulsation from bass
        self.BASS_RING_SENSITIVITY: int      = 100   # Strength of 3D ring radius pulsation from bass

        # Core
        self.CORE_BASE_SIZE: int             = 20    # Base size of the central core
        self.CORE_PULSE_AMOUNT: float        = 0.5   # Strength of the core's inherent, time-based pulse
        self.NUM_CORE_PULSES: int            = 6     # Number of high-energy radial pulses

        # Frequency Rays
        self.NUM_RAY_LAYERS: int             = 4     # Number of stacked ray layers for a 3D effect
        self.RAY_BASE_RADIUS: int            = 100   # Internal empty radius before rays start
        self.RAY_LENGTH_MULTIPLIER: int      = 250   # Max extension length for rays

        # Rings (3D Perspective)
        self.NUM_3D_RINGS: int               = 5     # Number of 3D wireframe rings
        self.RING_BASE_RADIUS: int           = 120   # Radius of the innermost 3D ring
        self.RING_SPACING: int               = 40    # Distance between 3D rings

        # Peaks (Energy Markers)
        self.PEAK_BASE_RADIUS: int           = 100   # Inner radius for peak markers
        self.PEAK_LENGTH_MULTIPLIER: int     = 280   # Max extension length for peak markers

        # HUD (Heads-Up Display)
        self.HUD_RADIUS: int                 = 280   # Outer radius for the main HUD grid
        self.HUD_SEGMENTS: int               = 12    # Number of segments in the HUD grid
        self.SHIELD_BASE_RADIUS: int         = 320   # Radius of the innermost outer 'shield' ring
        self.SHIELD_RING_SPACING: int        = 40    # Distance between 'shield' rings

        # Particles
        self.MAX_PARTICLES: int              = 75    # Maximum number of particles on screen
        self.PARTICLE_SPAWN_RATE: int        = 3     # Spawn rate multiplier based on average frequency
        self.PARTICLE_LIFESPAN: float        = 0.02  # Decay rate (1.0 / N frames) for particle life
        
        # --- End of Tweakables ---

        self.colors = {
            'background': (5, 5, 15),       # Dark, deep blue/black background
            'cyan': (0, 255, 255),          # Standard cyan
            'cyan_dark': (0, 150, 200),     # Darker cyan for subtle elements
            'cyan_bright': (100, 255, 255), # Bright cyan/white for highlights
            'blue': (50, 150, 255),         # Standard blue
            'grid': (20, 40, 70),           # Dark blue for grid/HUD lines
            'text': (200, 220, 255),        # Light blue/white for UI text
            'control': (100, 200, 255),     # Blue for control elements
            'glow': (150, 220, 255),        # Pale blue for glow effects
            'energy': (0, 200, 255),        # Blue for high-energy pulses
            'bass': (50, 150, 255),         # Color for bass frequencies
            'mid': (0, 220, 255),           # Color for mid frequencies
            'high': (200, 255, 255),        # Color for high frequencies
        }

        self.render_font = pygame.font.Font(None, 18)

        # State variables
        self.time_offset = 0    # Used for global rotation and animation time-slicing
        self.hud_rotation = 0   # Separate rotation state for HUD elements
        self.particles = []     # List to store active particle objects
    
    def _create_glowing_circle(self, radius, intensity):
        """
        Creates a pygame.Surface with a soft, anti-aliased glowing circle effect.
        The glow is achieved by drawing multiple concentric, fading circles.

        Args:
            radius (int): The base radius of the glow.
            intensity (float): A multiplier controlling the overall alpha/brightness (0.0 to 1.0+).

        Returns:
            pygame.Surface: The surface containing the glow effect.
        """
        size = int(radius * 3)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Draw circles from large to small, with alpha fading outwards (quadratic falloff)
        for r in range(size // 2, 0, -1):
            alpha = int(200 * intensity * (1 - r / (size // 2)) ** 2)
            color = (*self.colors['cyan'], alpha)
            pygame.draw.circle(surf, color, (center, center), r)
        return surf
    
    def _add_particle(self, x, y, freq_intensity):
        """
        Adds a new particle to the particle system, ejecting it outwards from (x, y).

        Args:
            x (float): Starting x-coordinate.
            y (float): Starting y-coordinate.
            freq_intensity (float): The frequency magnitude influencing the particle's speed.
        """
        angle = np.random.uniform(0, 2 * math.pi)
        # Particle speed is proportional to the energy that spawned it
        speed = np.random.uniform(1, 3) * freq_intensity
        particle = {
            'x': x, 'y': y,
            'vx': math.cos(angle) * speed, 'vy': math.sin(angle) * speed,
            'life': 1.0, 'size': np.random.uniform(1, 3)
        }
        self.particles.append(particle)
    
    def _update_particles(self):
        """Updates the position and lifetime of all active particles."""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            # Decay life
            particle['life'] -= self.PARTICLE_LIFESPAN
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def _draw_particles(self):
        """Renders all active particles to the screen with a fading effect."""
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            # Particle size also decays with life
            size = int(particle['size'] * particle['life'])
            if size > 0:
                color = (*self.colors['cyan_bright'], alpha)
                # Draw the particle as a small, anti-aliased circle
                surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (size * 2, size * 2), size)
                # Blit the particle surface to its position
                self.screen.blit(surf, (int(particle['x'] - size * 2), int(particle['y'] - size * 2)))
    
    def _draw_3d_ring(self, center_x, center_y, radius, tilt, rotation, thickness, color, segments=64):
        """
        Draws a 3D wireframe ring with perspective and basic shading.
        
        Args:
            center_x (int): X-coordinate of the center point.
            center_y (int): Y-coordinate of the center point.
            radius (float): The radius of the ring.
            tilt (float): Angle of tilt relative to the screen plane (e.g., math.pi / 6).
            rotation (float): Rotation angle around the center point.
            thickness (int): The line thickness.
            color (tuple): RGB color of the ring.
            segments (int, optional): Number of line segments to approximate the circle. Defaults to 64.
        """
        points = []
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi + rotation
            
            # 3D coordinates (X, Y, Z)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle) * math.cos(tilt) # Y projection based on tilt
            z = radius * math.sin(angle) * math.sin(tilt) # Z for depth

            # Perspective scaling: points further away (higher Z) are smaller
            scale = 1 / (1 + z / 500) 
            screen_x = center_x + x * scale
            screen_y = center_y + y * scale
            
            # Basic shading: points further back are darker
            brightness = (z + radius) / (2 * radius)
            points.append((screen_x, screen_y, brightness))
        
        # Draw the ring segments as lines
        for i in range(len(points)):
            x1, y1, b1 = points[i]
            x2, y2, b2 = points[(i + 1) % len(points)] # Connect to the next point (wrapping around)
            
            avg_brightness = (b1 + b2) / 2
            r, g, b = color
            # Apply brightness shading to the color
            shade_color = (int(r * avg_brightness), int(g * avg_brightness), int(b * avg_brightness))
            
            pygame.draw.line(self.screen, shade_color, (int(x1), int(y1)), (int(x2), int(y2)), thickness)

    def draw_circular_mode(self, frequencies):
        """
        Draws the main circular, holographic visualization based on audio frequencies.

        Args:
            frequencies (np.ndarray): An array of normalized frequency band magnitudes (0.0 to 1.0).
        """
        center_x = self.width // 2
        center_y = self.height // 1.8 # Slightly offset from center for vertical balance

        # Update global animation state
        self.time_offset += self.ROTATION_SPEED
        self.hud_rotation += self.HUD_ROTATION_SPEED

        # Calculate general energy levels
        avg_freq = np.mean(frequencies)
        bass_freq = np.mean(frequencies[:8]) # Average of the first 8 bands (low end)

        # ===== 1. 3D ROTATING RINGS (MULTI-LAYERED) =====
        for ring_idx in range(self.NUM_3D_RINGS):
            # Dynamic tilt and rotation
            tilt = math.pi / 6 + math.sin(self.time_offset + ring_idx) * 0.2 
            rotation = self.time_offset * (1 + ring_idx * 0.3)
            # Bass pulse affects the ring radius
            radius = (self.RING_BASE_RADIUS + ring_idx * self.RING_SPACING + 
                      bass_freq * self.BASS_RING_SENSITIVITY)
            # Thickness decreases with distance (ring_idx)
            thickness = max(1, int(3 - ring_idx * 0.3)) 
            
            alpha = int(150 - ring_idx * 20)
            color = (0, 200 + ring_idx * 10, 255, alpha)
            
            self._draw_3d_ring(center_x, center_y, radius, tilt, rotation, thickness, color[:3])

        # ===== 2. HOLOGRAPHIC INTERFERENCE WAVES (Dynamic Dot Patterns) =====
        wave_count = 8
        for wave_idx in range(wave_count):
            wave_angle = (wave_idx / wave_count) * 2 * math.pi + self.time_offset * 2
            wave_radius = 80 + wave_idx * 15
            for i in range(32):
                angle = (i / 32) * 2 * math.pi
                freq_val = frequencies[i]
                # Radius oscillates based on frequency and time offset
                offset_radius = wave_radius + freq_val * 60 * math.sin(self.time_offset * 3 + wave_idx)
                x = center_x + offset_radius * math.cos(angle + wave_angle)
                y = center_y + offset_radius * math.sin(angle + wave_angle)
                
                intensity = freq_val * 0.6
                color = (0, int(150 + 105 * intensity), int(200 + 55 * intensity))
                pygame.draw.circle(self.screen, color, (int(x), int(y)), 2)

        # ===== 3. MAIN FREQUENCY RAYS (3D Effect) =====
        for layer in range(self.NUM_RAY_LAYERS):
            layer_angle = self.time_offset * (1 + layer * 0.2)
            z_offset = layer * 30 # Simulated depth offset
            
            for i, freq in enumerate(frequencies):
                angle = (i / len(frequencies)) * 2 * math.pi + layer_angle
                
                base_radius = self.RAY_BASE_RADIUS + layer * 35
                freq_extension = freq * (self.RAY_LENGTH_MULTIPLIER - layer * 20)

                # Apply bass multiplier to low frequencies
                if i < 8:
                    freq_extension *= self.BASS_RAY_MULTIPLIER 

                total_radius = base_radius + freq_extension
                
                # Apply depth scaling
                depth_scale = 1 - (z_offset / 300)
                x = center_x + total_radius * math.cos(angle) * depth_scale
                y = center_y + total_radius * math.sin(angle) * depth_scale
                
                brightness = 0.6 + 0.4 * depth_scale
                
                # Color coding based on frequency band
                if i < 8:       # Bass
                    r, g, b = self.colors['bass']
                elif i < 22:    # Mids
                    r, g, b = self.colors['mid']
                else:           # Highs
                    r, g, b = self.colors['high']
                color = (int(r * brightness), int(g * brightness), int(b * brightness))
                
                thickness = max(1, int((4 - layer) * freq * 2)) # Thickness based on intensity and layer
                start_pos = (center_x, center_y)
                end_pos = (int(x), int(y))
                
                pygame.draw.line(self.screen, color, start_pos, end_pos, thickness)
                
                # Particle spawning (ejection from ray tips)
                if freq > 0.5 and np.random.random() > 0.9:
                    self._add_particle(x, y, freq)

        # ===== 4. FREQUENCY PEAKS (ENERGY PULSES) =====
        # Uses the processed peak data for visual flare
        for i, (freq, peak) in enumerate(zip(frequencies, self.audio_processor.peak_frequencies)):
            angle = (i / len(frequencies)) * 2 * math.pi + self.time_offset * 0.5
            
            peak_radius = self.PEAK_BASE_RADIUS + peak * self.PEAK_LENGTH_MULTIPLIER
            x_peak = center_x + peak_radius * math.cos(angle)
            y_peak = center_y + peak_radius * math.sin(angle)
            
            pulse = 1 + 0.3 * math.sin(self.time_offset * 10 + i)
            peak_size = int(4 * pulse)
            
            pygame.draw.circle(self.screen, self.colors['cyan_bright'], (int(x_peak), int(y_peak)), peak_size)
            
            if peak > 0.7:
                # Add a strong glow for high peaks
                glow_surf = self._create_glowing_circle(peak_size * 2, peak)
                glow_rect = glow_surf.get_rect(center=(int(x_peak), int(y_peak)))
                self.screen.blit(glow_surf, glow_rect)

        # ===== 5. ROTATING HUD ELEMENTS (Inner Grid) =====
        for i in range(self.HUD_SEGMENTS):
            angle = (i / self.HUD_SEGMENTS) * 2 * math.pi + self.hud_rotation
            
            # Draw radial ticks
            x1 = center_x + self.HUD_RADIUS * math.cos(angle)
            y1 = center_y + self.HUD_RADIUS * math.sin(angle)
            x2 = center_x + (self.HUD_RADIUS + 15) * math.cos(angle)
            y2 = center_y + (self.HUD_RADIUS + 15) * math.sin(angle)
            
            pygame.gfxdraw.line(self.screen, int(x1), int(y1), int(x2), int(y2), self.colors['grid'])
            
            # Draw segmented arcs
            if i % 3 == 0:
                next_angle = ((i + 1) / self.HUD_SEGMENTS) * 2 * math.pi + self.hud_rotation
                arc_points = []
                for j in range(10):
                    t = j / 9
                    a = angle + (next_angle - angle) * t # Interpolate angle
                    x = center_x + self.HUD_RADIUS * math.cos(a)
                    y = center_y + self.HUD_RADIUS * math.sin(a)
                    arc_points.append((int(x), int(y)))
                
                if len(arc_points) > 1:
                    for j in range(len(arc_points) - 1):
                        pygame.gfxdraw.line(self.screen, 
                                            arc_points[j][0], arc_points[j][1],
                                            arc_points[j+1][0], arc_points[j+1][1],
                                            self.colors['grid'])

        # ===== 6. CENTRAL CORE (REACTOR) =====
        core_pulse = 1 + self.CORE_PULSE_AMOUNT * math.sin(self.time_offset * 5)
        # Core size driven by base size, bass energy, and time-based pulse
        core_size = int((self.CORE_BASE_SIZE + bass_freq * self.BASS_CORE_SENSITIVITY) * core_pulse)
        
        # Draw multiple concentric circles for a layered glow
        for layer_size in range(core_size, 0, -5):
            alpha = int(200 * (layer_size / core_size))
            color = (*self.colors['cyan_bright'], alpha)
            surf = pygame.Surface((layer_size * 2, layer_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (layer_size, layer_size), layer_size)
            self.screen.blit(surf, (center_x - layer_size, center_y - layer_size))
        
        # Inner white center
        pygame.draw.circle(self.screen, (255, 255, 255), (int(center_x), int(center_y)), core_size // 3)
        
        # Outer glow field
        field_intensity = 0.8 + avg_freq * 0.4
        field_surf = self._create_glowing_circle(core_size * 2, field_intensity)
        field_rect = field_surf.get_rect(center=(center_x, center_y))
        self.screen.blit(field_surf, field_rect)

        # ===== 7. ENERGY PULSES (from core) =====
        # Triggered by high overall energy
        if avg_freq > 0.6:
            for pulse_idx in range(self.NUM_CORE_PULSES):
                pulse_angle = (pulse_idx / self.NUM_CORE_PULSES) * 2 * math.pi + self.time_offset * 3
                # Pulse distance is calculated using modulo for a continuous loop
                pulse_distance = (self.time_offset * 100) % 250
                
                x = center_x + pulse_distance * math.cos(pulse_angle)
                y = center_y + pulse_distance * math.sin(pulse_angle)
                
                # Alpha and size fade as the pulse moves outward
                alpha = int(255 * (1 - pulse_distance / 250))
                color = (*self.colors['energy'], alpha)
                size = int(5 * (1 - pulse_distance / 250))
                
                if size > 0:
                    surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                    pygame.draw.circle(surf, color, (size * 2, size * 2), size)
                    self.screen.blit(surf, (int(x - size * 2), int(y - size * 2)))

        # ===== 8. PARTICLE SYSTEM =====
        self._update_particles()
        self._draw_particles()
        
        # Spawn new particles if below max and energy is high
        if len(self.particles) < self.MAX_PARTICLES and avg_freq > 0.3:
            num_new = int(avg_freq * self.PARTICLE_SPAWN_RATE)
            for _ in range(num_new):
                # Particles spawn randomly around a radius
                angle = np.random.uniform(0, 2 * math.pi)
                distance = np.random.uniform(50, 150)
                x = center_x + distance * math.cos(angle)
                y = center_y + distance * math.sin(angle)
                self._add_particle(x, y, avg_freq)

        # ===== 9. OUTER SHIELD RINGS (Outer Decorative Rings) =====
        for ring_idx in range(3):
            ring_radius = self.SHIELD_BASE_RADIUS + ring_idx * self.SHIELD_RING_SPACING
            segments = 60
            for i in range(segments):
                if i % 5 != 0: # Only draw every 5th segment for a dashed/broken effect
                    continue
                    
                angle = (i / segments) * 2 * math.pi - self.hud_rotation * (1 + ring_idx * 0.5)
                x = center_x + ring_radius * math.cos(angle)
                y = center_y + ring_radius * math.sin(angle)
                
                pygame.draw.circle(self.screen, self.colors['grid'], (int(x), int(y)), 2)

    def draw_ui(self):
        """Draws all user interface elements (e.g., FPS counter)."""

        # Draw FPS counter
        fps_text = f"FPS: {int(self.clock.get_fps())}"
        fps_surface = self.render_font.render(fps_text, True,
                                             self.colors['text'])
        # Position in the top-right corner
        self.screen.blit(fps_surface, (self.width-fps_surface.get_width()-20, 20))

    def update(self):
        """Called once per frame. Fetches data, updates all visual states, and draws the scene."""
        frequencies = self.audio_processor.process() # Get the latest frequency data
        self.screen.fill(self.colors['background'])
        self.draw_circular_mode(frequencies)
        self.draw_ui()
        pygame.display.flip() # Update the full screen
        self.clock.tick(self.FPS) # Limit frame rate

    def handle_events(self):
        """Processes all user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    self.audio_processor.stop() # Stop audio playback on exit

    def run(self):
        """The main application loop."""
        try:
            while self.running:
                self.handle_events()
                self.update()
        finally:
            # Clean up resources regardless of how the loop exited
            self.audio_processor.stop()
            pygame.quit()
    
    def play_audio(self, audio_file: str) -> float:
        """
        Loads an audio file into the processor and begins playback.

        Args:
            audio_file (str): The path to the audio file.

        Returns:
            float: The duration of the loaded audio file in seconds.
        """
        duration = self.audio_processor.add_audio(audio_file)
        self.audio_processor.play()

        return duration