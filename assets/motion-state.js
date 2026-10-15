export function motionAllowed({paused,reduced,visible,inView=true}) {
  return !paused && !reduced && visible && inView;
}
