import { expect, test } from "vitest";
import { version } from "./index";

test("version returns the placeholder", () => {
  expect(version()).toBe("0.0.0");
});
