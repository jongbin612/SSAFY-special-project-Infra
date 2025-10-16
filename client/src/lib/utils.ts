import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function drawLine(
  ctx: CanvasRenderingContext2D,
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  color: string,
  thickness = 2,
) {
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.strokeStyle = color;
  ctx.lineWidth = thickness;
  ctx.stroke();
}

// Helper function to draw a circle on the canvas
export function drawCircle(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  radius: number,
  color: string,
) {
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, 2 * Math.PI);
  ctx.fillStyle = color;
  ctx.fill();
}

// Function to determine if shoulders are level
export function shouldersLevel(
  leftShoulder: { y: number },
  rightShoulder: { y: number },
  threshold = 0.05,
) {
  return Math.abs(leftShoulder.y - rightShoulder.y) < threshold;
}

// Function to determine if the back is straight
export function backStraight(
  shoulder: { y: number; x: number },
  hip: { y: number; x: number },
  knee: { y: number; x: number },
  threshold = 0.1,
) {
  const upperAngle = Math.atan2(hip.y - shoulder.y, hip.x - shoulder.x);
  const lowerAngle = Math.atan2(knee.y - hip.y, knee.x - hip.x);
  return Math.abs(upperAngle - lowerAngle) < threshold;
}
