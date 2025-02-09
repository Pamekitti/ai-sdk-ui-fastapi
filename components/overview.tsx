import { motion } from "framer-motion";
import Link from "next/link";

import { MessageIcon } from "./icons";

export const Overview = () => {
  return (
    <motion.div
      key="overview"
      className="max-w-3xl mx-auto md:mt-20"
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ delay: 0.5 }}
    >
      <div className="rounded-xl p-6 flex flex-col gap-8 leading-relaxed text-center max-w-xl">
        <p className="flex flex-row justify-center gap-4 items-center">
          <MessageIcon size={32} />
        </p>
        <p>
          Welcome to Alto CERO AI Assistant, your intelligent companion for building management. Powered by{" "}
          <Link
            className="font-medium underline underline-offset-4"
            href="https://altotech.ai"
            target="_blank"
          >
            AltoTech Global
          </Link>
        </p>
        <p>
          Our AI assistant provides real-time insights and intelligent building management solutions to optimize your facility operations, with seamless integration into existing systems.
        </p>
      </div>
    </motion.div>
  );
};
