"use strict";
(async () => {
  window.resizeTo(1280, 720); // best effort for app windows; actual size is recorded
  const config = await (await fetch("/bench/config", { cache: "no-store" })).json();
  let measureStart = null, previous = null, sent = false;
  const intervals = [];
  window.chonoiFrame = (at, snapshot) => {
    if (sent || !snapshot || snapshot.mode !== "gather" || snapshot.error) return;
    const first = window.chonoiFirstFrame;
    if (!first || at - first.at < config.warmup_s * 1000) return;
    if (document.hidden) {
      sent = true;
      fetch("/bench/result", { method: "POST", body: JSON.stringify({error:"Benchmark tab became hidden"}) });
      return;
    }
    if (measureStart === null) { measureStart = at; previous = at; return; }
    intervals.push((at - previous) / 1000);
    previous = at;
    const elapsed = (at - measureStart) / 1000;
    if (elapsed >= config.duration_s) {
      sent = true;
      fetch("/bench/result", { method: "POST", headers: {"Content-Type":"application/json"},
        body: JSON.stringify({intervals_s:intervals, measured_s:elapsed,
          first_frame_epoch_ms:first.epoch, canvas:[cv.width,cv.height],
          outer_window:[outerWidth,outerHeight], hidden:document.hidden,
          scene:"gather", fish_count:(snapshot.fish||[]).length,
          monster_count:(snapshot.monsters||[]).length, player_pos:snapshot.player.pos}) });
    }
  };
})().catch((error) => fetch("/bench/result", {method:"POST",body:JSON.stringify({error:String(error)})}));
