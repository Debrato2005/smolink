import { useEffect, useRef } from 'react';

const CELL_SIZE = 64;
const PROXIMITY = 200;
const POINTER_STRENGTH = 1800;
const VELOCITY_FILTER = 0.22;
const RETURN_DURATION = 1.15;
const BOUNCE = 0.18;
const TENSION = 0.24;
const MAX_DISPLACEMENT = 16;
const SHOCK_RADIUS = 280;
const SHOCK_STRENGTH = 1;

type Shock = { x: number; y: number; start: number };

export function SquareGrid() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const context = canvas.getContext('2d', { alpha: false });
    if (!context) return;
    canvas.dataset.renderer = 'canvas-2d';

    const rootStyle = getComputedStyle(document.documentElement);
    const background =
      rootStyle.getPropertyValue('--sky-surface').trim() || '#dfe9fb';
    const baseColor =
      rootStyle.getPropertyValue('--grid-line').trim() || '#c3d3ee';
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const precisePointerQuery = window.matchMedia('(hover: hover)');

    const view = { width: 0, height: 0, ratio: 1 };
    const grid = { count: 0, cols: 1, rows: 1 };
    const pointer = {
      x: 0,
      y: 0,
      vx: 0,
      vy: 0,
      time: 0,
      inside: false,
    };
    const shocks: Shock[] = [];

    let rest = new Float32Array(0);
    let offset = new Float32Array(0);
    let velocity = new Float32Array(0);
    let force = new Float32Array(0);
    let nextVelocity = new Float32Array(0);
    let wave = new Float32Array(0);
    let visible = true;
    let frameRequest = 0;
    let lastFrame = 0;

    const smootherstep = (value: number) => {
      const x = Math.min(1, Math.max(0, value));
      return x * x * x * (x * (x * 6 - 15) + 10);
    };
    const valueAt = (values: Float32Array, index: number) => values[index] ?? 0;

    const rebuild = () => {
      const startX = -CELL_SIZE;
      const startY = -CELL_SIZE;
      const cols = Math.ceil((view.width - startX) / CELL_SIZE) + 1;
      const rows = Math.ceil((view.height - startY) / CELL_SIZE) + 1;
      const count = cols * rows;

      rest = new Float32Array(count * 2);
      offset = new Float32Array(count * 2);
      velocity = new Float32Array(count * 2);
      force = new Float32Array(count * 2);
      nextVelocity = new Float32Array(count * 2);
      wave = new Float32Array(count * 4);

      for (let row = 0; row < rows; row += 1) {
        for (let column = 0; column < cols; column += 1) {
          const index = (row * cols + column) * 2;
          rest[index] = startX + column * CELL_SIZE;
          rest[index + 1] = startY + row * CELL_SIZE;
        }
      }

      Object.assign(grid, { count, cols, rows });
    };

    const draw = () => {
      context.setTransform(view.ratio, 0, 0, view.ratio, 0, 0);
      context.fillStyle = background;
      context.fillRect(0, 0, view.width, view.height);

      const pointPosition = (index: number) => {
        const point = index * 2;
        const wavePoint = index * 4;
        return {
          x:
            valueAt(rest, point) +
            valueAt(offset, point) +
            valueAt(wave, wavePoint),
          y:
            valueAt(rest, point + 1) +
            valueAt(offset, point + 1) +
            valueAt(wave, wavePoint + 1),
        };
      };

      context.strokeStyle = baseColor;
      context.lineWidth = 1;
      context.lineCap = 'round';
      context.lineJoin = 'round';
      context.beginPath();

      const traceSpline = (
        count: number,
        indexAt: (position: number) => number,
      ) => {
        if (count < 2) return;
        const first = pointPosition(indexAt(0));
        context.moveTo(first.x, first.y);

        for (let position = 0; position < count - 1; position += 1) {
          const start = pointPosition(indexAt(position));
          const end = pointPosition(indexAt(position + 1));
          const before = pointPosition(indexAt(Math.max(0, position - 1)));
          const after = pointPosition(
            indexAt(Math.min(count - 1, position + 2)),
          );

          context.bezierCurveTo(
            start.x + (end.x - before.x) / 6,
            start.y + (end.y - before.y) / 6,
            end.x - (after.x - start.x) / 6,
            end.y - (after.y - start.y) / 6,
            end.x,
            end.y,
          );
        }
      };

      for (let row = 0; row < grid.rows; row += 1) {
        traceSpline(grid.cols, (column) => row * grid.cols + column);
      }
      for (let column = 0; column < grid.cols; column += 1) {
        traceSpline(grid.rows, (row) => row * grid.cols + column);
      }
      context.stroke();
    };

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      view.width = Math.max(1, Math.round(rect.width));
      view.height = Math.max(1, Math.round(rect.height));
      view.ratio = ratio;
      canvas.width = Math.round(view.width * ratio);
      canvas.height = Math.round(view.height * ratio);
      rebuild();
      draw();
    };

    const clearMotion = () => {
      offset.fill(0);
      velocity.fill(0);
      force.fill(0);
      nextVelocity.fill(0);
      wave.fill(0);
      shocks.length = 0;
      pointer.vx = 0;
      pointer.vy = 0;
      pointer.time = 0;
      pointer.inside = false;
      draw();
    };

    const step = (delta: number, now: number) => {
      const dampingRatio = 1 - 0.85 * BOUNCE;
      const frequency = 4 / (dampingRatio * RETURN_DURATION);
      const stiffness = frequency * frequency;
      const damping = 2 * dampingRatio * frequency;
      const speed = Math.hypot(pointer.vx, pointer.vy);
      const drive =
        pointer.inside && precisePointerQuery.matches
          ? POINTER_STRENGTH * Math.tanh(speed / 1200)
          : 0;
      const directionX = speed > 0.001 ? pointer.vx / speed : 0;
      const directionY = speed > 0.001 ? pointer.vy / speed : 0;
      const waveWidth = CELL_SIZE * 1.4;
      const waveTravel = 440;
      const activeShocks = shocks.map((shock) => {
        const front = ((now - shock.start) / 1000) * waveTravel;
        const power = smootherstep(1 - front / SHOCK_RADIUS);
        return {
          ...shock,
          front,
          amplitude: power * SHOCK_STRENGTH * CELL_SIZE * 0.24,
        };
      });
      const coupling = (TENSION * 900) ** 2 / CELL_SIZE ** 2;
      const viscosity = Math.sqrt(coupling) * 0.06;
      const limit =
        Math.sqrt(stiffness + 8 * coupling) + damping + 8 * viscosity;
      const steps = Math.min(
        24,
        Math.max(1, Math.ceil(delta / Math.min(1 / 120, 1.2 / limit))),
      );
      const interval = delta / steps;

      for (let index = 0; index < grid.count; index += 1) {
        const point = index * 2;
        const restX = valueAt(rest, point);
        const restY = valueAt(rest, point + 1);
        let accelerationX = 0;
        let accelerationY = 0;

        if (drive > 0) {
          const distanceX = restX + valueAt(offset, point) - pointer.x;
          const distanceY = restY + valueAt(offset, point + 1) - pointer.y;
          const distance = Math.hypot(distanceX, distanceY);
          if (distance < PROXIMITY) {
            const weight = smootherstep(1 - distance / PROXIMITY) * drive;
            const normalX = distance > 0.001 ? distanceX / distance : 0;
            const normalY = distance > 0.001 ? distanceY / distance : 0;
            accelerationX += weight * (directionX * 0.25 + normalX * 0.9);
            accelerationY += weight * (directionY * 0.25 + normalY * 0.9);
          }
        }

        let waveX = 0;
        let waveY = 0;
        let waveVelocityX = 0;
        let waveVelocityY = 0;
        for (const shock of activeShocks) {
          if (shock.amplitude <= 0) continue;
          const distanceX = restX - shock.x;
          const distanceY = restY - shock.y;
          const distance = Math.hypot(distanceX, distanceY);
          const position = (distance - shock.front) / waveWidth;
          if (Math.abs(position) >= 3 || distance <= 0.001) continue;

          const normalX = distanceX / distance;
          const normalY = distanceY / distance;
          const profile = Math.exp(-position * position);
          const push = shock.amplitude * profile;
          const rate =
            ((shock.amplitude * 2 * position * profile) / waveWidth) *
            waveTravel;
          waveX += normalX * push;
          waveY += normalY * push;
          waveVelocityX += normalX * rate;
          waveVelocityY += normalY * rate;
          accelerationX += normalX * push * stiffness * 0.35;
          accelerationY += normalY * push * stiffness * 0.35;
        }

        force[point] = accelerationX;
        force[point + 1] = accelerationY;
        const wavePoint = index * 4;
        wave[wavePoint] = waveX;
        wave[wavePoint + 1] = waveY;
        wave[wavePoint + 2] = waveVelocityX;
        wave[wavePoint + 3] = waveVelocityY;
      }

      const rowStride = grid.cols * 2;
      for (let substep = 0; substep < steps; substep += 1) {
        for (let row = 0; row < grid.rows; row += 1) {
          for (let column = 0; column < grid.cols; column += 1) {
            const point = (row * grid.cols + column) * 2;
            let accelerationX =
              valueAt(force, point) -
              stiffness * valueAt(offset, point) -
              damping * valueAt(velocity, point);
            let accelerationY =
              valueAt(force, point + 1) -
              stiffness * valueAt(offset, point + 1) -
              damping * valueAt(velocity, point + 1);

            let laplacianX = -4 * valueAt(offset, point);
            let laplacianY = -4 * valueAt(offset, point + 1);
            let velocityMixX = -4 * valueAt(velocity, point);
            let velocityMixY = -4 * valueAt(velocity, point + 1);
            if (column > 0) {
              laplacianX += valueAt(offset, point - 2);
              laplacianY += valueAt(offset, point - 1);
              velocityMixX += valueAt(velocity, point - 2);
              velocityMixY += valueAt(velocity, point - 1);
            }
            if (column < grid.cols - 1) {
              laplacianX += valueAt(offset, point + 2);
              laplacianY += valueAt(offset, point + 3);
              velocityMixX += valueAt(velocity, point + 2);
              velocityMixY += valueAt(velocity, point + 3);
            }
            if (row > 0) {
              laplacianX += valueAt(offset, point - rowStride);
              laplacianY += valueAt(offset, point - rowStride + 1);
              velocityMixX += valueAt(velocity, point - rowStride);
              velocityMixY += valueAt(velocity, point - rowStride + 1);
            }
            if (row < grid.rows - 1) {
              laplacianX += valueAt(offset, point + rowStride);
              laplacianY += valueAt(offset, point + rowStride + 1);
              velocityMixX += valueAt(velocity, point + rowStride);
              velocityMixY += valueAt(velocity, point + rowStride + 1);
            }
            accelerationX += coupling * laplacianX + viscosity * velocityMixX;
            accelerationY += coupling * laplacianY + viscosity * velocityMixY;
            nextVelocity[point] =
              valueAt(velocity, point) + accelerationX * interval;
            nextVelocity[point + 1] =
              valueAt(velocity, point + 1) + accelerationY * interval;
          }
        }

        for (let point = 0; point < offset.length; point += 2) {
          velocity[point] = valueAt(nextVelocity, point);
          velocity[point + 1] = valueAt(nextVelocity, point + 1);
          offset[point] =
            valueAt(offset, point) + valueAt(velocity, point) * interval;
          offset[point + 1] =
            valueAt(offset, point + 1) +
            valueAt(velocity, point + 1) * interval;

          const displacement = Math.hypot(
            valueAt(offset, point),
            valueAt(offset, point + 1),
          );
          if (displacement > MAX_DISPLACEMENT) {
            const scale = MAX_DISPLACEMENT / displacement;
            offset[point] = valueAt(offset, point) * scale;
            offset[point + 1] = valueAt(offset, point + 1) * scale;
            velocity[point] = valueAt(velocity, point) * 0.7;
            velocity[point + 1] = valueAt(velocity, point + 1) * 0.7;
          }
        }
      }

      for (let index = shocks.length - 1; index >= 0; index -= 1) {
        if ((activeShocks[index]?.front ?? 0) > SHOCK_RADIUS + waveWidth * 3) {
          shocks.splice(index, 1);
        }
      }

      const velocityDecay = 1 - Math.exp(-delta / 0.08);
      pointer.vx -= pointer.vx * velocityDecay;
      pointer.vy -= pointer.vy * velocityDecay;
    };

    const settled = () => {
      if (shocks.length) return false;
      if (Math.abs(pointer.vx) + Math.abs(pointer.vy) > 1) return false;
      for (let index = 0; index < offset.length; index += 1) {
        if (Math.abs(valueAt(offset, index)) > 0.02) return false;
        if (Math.abs(valueAt(velocity, index)) > 0.5) return false;
      }
      return true;
    };

    const animate = (now: number) => {
      frameRequest = 0;
      if (!visible || motionQuery.matches) return;
      const delta = Math.min(0.05, (now - lastFrame) / 1000 || 0);
      lastFrame = now;
      step(delta, now);
      draw();
      if (!settled()) frameRequest = requestAnimationFrame(animate);
    };

    const wake = () => {
      if (frameRequest || !visible || motionQuery.matches) return;
      lastFrame = performance.now();
      frameRequest = requestAnimationFrame(animate);
    };

    const locate = (event: PointerEvent) => {
      const rect = canvas.getBoundingClientRect();
      return [event.clientX - rect.left, event.clientY - rect.top] as const;
    };

    const onPointerMove = (event: PointerEvent) => {
      if (motionQuery.matches || event.pointerType === 'touch') return;
      const [x, y] = locate(event);
      const inside = x >= 0 && y >= 0 && x <= view.width && y <= view.height;
      const time = event.timeStamp || performance.now();

      if (inside && pointer.inside && pointer.time) {
        const elapsed = Math.max(4, time - pointer.time) / 1000;
        const velocityX = (x - pointer.x) / elapsed;
        const velocityY = (y - pointer.y) / elapsed;
        pointer.vx += (velocityX - pointer.vx) * VELOCITY_FILTER;
        pointer.vy += (velocityY - pointer.vy) * VELOCITY_FILTER;
      } else {
        pointer.vx = 0;
        pointer.vy = 0;
      }

      pointer.x = x;
      pointer.y = y;
      pointer.time = time;
      pointer.inside = inside;
      if (inside) wake();
    };

    const leave = () => {
      pointer.inside = false;
      pointer.time = 0;
      wake();
    };

    const onPointerOut = (event: PointerEvent) => {
      if (!event.relatedTarget) leave();
    };

    const onPointerDown = (event: PointerEvent) => {
      if (motionQuery.matches || !event.isPrimary) return;
      const [x, y] = locate(event);
      if (x < 0 || y < 0 || x > view.width || y > view.height) return;
      shocks.push({ x, y, start: performance.now() });
      if (shocks.length > 6) shocks.shift();
      wake();
    };

    const onMotionPreference = () => {
      cancelAnimationFrame(frameRequest);
      frameRequest = 0;
      clearMotion();
    };

    const resizeObserver = new ResizeObserver(() => resize());
    resizeObserver.observe(canvas);

    const visibilityObserver = new IntersectionObserver(([entry]) => {
      visible = entry?.isIntersecting ?? false;
      if (visible) wake();
    });
    visibilityObserver.observe(canvas);

    const onVisibilityChange = () => {
      if (document.hidden) {
        cancelAnimationFrame(frameRequest);
        frameRequest = 0;
      } else {
        wake();
      }
    };

    window.addEventListener('pointermove', onPointerMove, { passive: true });
    window.addEventListener('pointerdown', onPointerDown, { passive: true });
    window.addEventListener('pointerout', onPointerOut);
    window.addEventListener('blur', leave);
    document.addEventListener('visibilitychange', onVisibilityChange);
    motionQuery.addEventListener('change', onMotionPreference);
    resize();

    return () => {
      cancelAnimationFrame(frameRequest);
      resizeObserver.disconnect();
      visibilityObserver.disconnect();
      window.removeEventListener('pointermove', onPointerMove);
      window.removeEventListener('pointerdown', onPointerDown);
      window.removeEventListener('pointerout', onPointerOut);
      window.removeEventListener('blur', leave);
      document.removeEventListener('visibilitychange', onVisibilityChange);
      motionQuery.removeEventListener('change', onMotionPreference);
    };
  }, []);

  return (
    <div className="square-grid" data-square-grid aria-hidden="true">
      <canvas ref={canvasRef} className="square-grid-canvas" />
    </div>
  );
}
