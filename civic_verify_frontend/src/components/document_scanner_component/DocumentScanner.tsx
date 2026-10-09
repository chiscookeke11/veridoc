"use client";

import { useEffect, useRef, useState } from "react";
import s from "./DocumentScanner.module.css";

export type ScanDoc = {
  title: string;
  id: string;
  type: string; // e.g. "academic.degree"
  fields: [string, string, string]; // issuing authority, holder, seal/signature
  checks: [boolean, boolean, boolean]; // result of each field check
  score: number; // 0-100
  grade: string; // "A" ... "F"
  status: string; // "Issued 2019", "Expired 2023" ...
};

export const DEFAULT_DOCS: ScanDoc[] = [
  { title: "Degree Certificate", id: "doc_UNN-2019-4471", type: "academic.degree", fields: ["Univ. of Nigeria", "Ada Nwosu", "Registrar e-seal"], checks: [true, true, true], score: 96, grade: "A", status: "Issued 2019" },
  { title: "Business Registration", id: "doc_CAC-1048832", type: "business.registration", fields: ["CAC", "Fundflow Ltd", "CAC digital stamp"], checks: [true, true, true], score: 91, grade: "A", status: "Active" },
  { title: "International Passport", id: "doc_NIS-A09127733", type: "identity.passport", fields: ["Immigration Service", "Tunde Bello", "Biometric chip"], checks: [true, true, true], score: 94, grade: "A", status: "Valid to 2031" },
  { title: "Tax Clearance", id: "doc_FIRS-TCC-5521", type: "tax.clearance", fields: ["FIRS", "Cascade Traders", "Signature mismatch"], checks: [true, true, false], score: 38, grade: "F", status: "Flagged" },
  { title: "Practising License", id: "doc_MDCN-77120", type: "professional.license", fields: ["MDCN", "Dr. Amaka Eze", "Seal expired"], checks: [true, true, false], score: 44, grade: "D", status: "Expired 2023" },
];

const LABELS = ["ISSUING AUTHORITY", "HOLDER", "SEAL & SIGNATURE"];
const W = 236; // mini card width (keep in sync with CSS)
const GAP = 16;
const isGood = (d: ScanDoc) => d.checks.every(Boolean) && d.score >= 50;
const cx = (...c: (string | false | undefined)[]) => c.filter(Boolean).join(" ");

type Props = { docs?: ScanDoc[]; loop?: boolean; className?: string };

export default function DocumentScanner({ docs = DEFAULT_DOCS, loop = true, className }: Props) {
  const n = docs.length;
  const stageRef = useRef<HTMLDivElement>(null);
  const [stageW, setStageW] = useState(1000);
  const [pos, setPos] = useState(n - 1 + 1.2);
  const [noTrans, setNoTrans] = useState(true);
  const [heroIdx, setHeroIdx] = useState<number | null>(null);
  const [hiddenIdx, setHiddenIdx] = useState<number | null>(null);
  const [heroOff, setHeroOff] = useState(true);
  const [rowsIn, setRowsIn] = useState(false);
  const [lit, setLit] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [resolved, setResolved] = useState<(boolean | null)[]>([null, null, null]);
  const [ring, setRing] = useState(0);
  const [ringState, setRingState] = useState<"" | "done" | "bad">("");
  const [verdicts, setVerdicts] = useState<(boolean | undefined)[]>([]);
  const [lastBad, setLastBad] = useState(false);

  // track the container width so the scanner stays centred
  useEffect(() => {
    const el = stageRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setStageW(el.clientWidth));
    ro.observe(el);
    setStageW(el.clientWidth);
    return () => ro.disconnect();
  }, []);

  // the animation timeline
  useEffect(() => {
    let cancelled = false;
    const wait = (ms: number) =>
      new Promise<void>((res, rej) => setTimeout(() => (cancelled ? rej() : res()), ms));

    (async () => {
      try {
        do {
          // reset (instantly, no slide), cards start off to the left
          setNoTrans(true);
          setVerdicts([]);
          setHeroOff(true);
          setHiddenIdx(null);
          setPos(n - 1 + 1.2);
          await wait(60);
          setNoTrans(false);

          for (let i = 0; i < n; i++) {
            const d = docs[i];
            const ok = isGood(d);
            setHeroOff(true);
            setHiddenIdx(null);
            setRowsIn(false);
            setPos(n - 1 - i); // slide the track so doc i sits under the scanner
            await wait(900);

            setHiddenIdx(i);
            setHeroIdx(i);
            setResolved([null, null, null]);
            setRing(0);
            setRingState("");
            setLit(false);
            setLastBad(!ok);
            await wait(60);
            setHeroOff(false);
            await wait(350);

            setScanning(true);
            setRowsIn(true);
            await wait(450);
            setLit(true);

            let count = 0;
            await Promise.all(
              [1100, 1800, 2500].map(async (t, k) => {
                await wait(t);
                setResolved((r) => r.map((v, j) => (j === k ? d.checks[k] : v)));
                count++;
                setRing(count / 3);
              })
            );
            setScanning(false);
            await wait(250);
            setRingState(ok ? "done" : "bad");
            setRing(1);
            setVerdicts((v) => {
              const c = [...v];
              c[i] = ok;
              return c;
            });
            await wait(1500);
          }

          setHeroOff(true);
          setHiddenIdx(null);
          setPos(-1.6); // push everything off to the right
          await wait(2200);
        } while (loop);
      } catch {
        /* unmounted */
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [docs, loop, n]);

  const hd = docs[heroIdx ?? 0];
  const order = docs.map((_, i) => i).reverse(); // scan order runs left -> right
  const tx = stageW / 2 - (pos * (W + GAP) + W / 2);

  return (
    <div ref={stageRef} className={cx(s.stage, scanning && s.scanning, className)}>
      <div className={cx(s.glow, s.glowL)} />
      <div className={cx(s.glow, s.glowR, lastBad && s.bad)} />
      <div className={s.frame}><b>+</b><b>+</b></div>
      <div className={s.dots} />

      <div className={cx(s.track, noTrans && s.nt)} style={{ transform: `translate(${tx}px,-50%)` }}>
        {order.map((i) => {
          const d = docs[i];
          const v = verdicts[i];
          const done = v !== undefined;
          return (
            <div key={d.id} className={cx(s.mini, hiddenIdx === i && s.hid, v === true && s.ok)}>
              <h4>
                {d.title}
                {done && <span className={cx(s.pill, v ? s.ok : s.no)}>{v ? "✓ Verified" : "✕ Rejected"}</span>}
              </h4>
              <div className={s.mrow}>DOC NO.<b>{d.id}</b></div>
              <div className={s.mrow}>ISSUER<b>{done ? d.fields[0] : "—"}</b></div>
              <div className={s.mrow}>HOLDER<b>{done ? d.fields[1] : "—"}</b></div>
              <div className={s.mrow}>SEAL<b>{done ? d.fields[2] : "—"}</b></div>
              <div className={s.mrow}>STATUS<b>{done ? d.status : "—"}</b></div>
            </div>
          );
        })}
      </div>

      <div className={cx(s.hero, heroOff && s.off)}>
        <div className={s.card}>
          <div className={s.hd}>
            <div>
              <h2>{hd.title}</h2>
              <div className={s.sub}>{hd.type}</div>
            </div>
            <svg className={cx(s.ring, ringState === "done" && s.done, ringState === "bad" && s.bad)} viewBox="0 0 42 42">
              <circle className={s.ringBg} cx="21" cy="21" r="18" />
              <circle className={s.ringFg} cx="21" cy="21" r="18" style={{ strokeDashoffset: 113 * (1 - ring) }} />
              <path d="M13 21.5l6 6 11-12" />
            </svg>
          </div>

          <div className={s.cred}>
            <p className={cx(s.credLabel, lit && s.lit)}>document no: <span>{hd.id}</span></p>
            {[0, 1, 2].map((k) => (
              <div key={k} className={cx(s.row, rowsIn && s.in)}>
                <div>
                  <small>{LABELS[k]}</small>
                  <div className={s.v}>{hd.fields[k]}</div>
                </div>
                <div className={s.sl}>
                  {resolved[k] === null ? (
                    <div className={s.ld}><i /><i /><i /><i /></div>
                  ) : (
                    <span className={cx(s.pill, resolved[k] ? s.ok : s.no)}>{resolved[k] ? "✓ Verified" : "✕ Rejected"}</span>
                  )}
                </div>
              </div>
            ))}
            <div className={cx(s.row, rowsIn && s.in)}>
              <div>
                <small>AUTHENTICITY SCORE</small>
                <span className={s.tag}>Grade {hd.grade}</span>
              </div>
              <div className={s.sc}><b>{hd.score}</b><span>/100</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
