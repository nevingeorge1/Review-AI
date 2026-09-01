import { CODE_SAMPLES } from '../data/samples';

describe('Frontend Code Samples Validation', () => {
  test('all curated samples are non-empty and within assessment limits', () => {
    expect(CODE_SAMPLES.length).toBeGreaterThanOrEqual(4);

    for (const sample of CODE_SAMPLES) {
      expect(sample.id).toBeTruthy();
      expect(sample.name).toBeTruthy();
      expect(sample.filename.endsWith('.py')).toBe(true);
      expect(sample.code.length).toBeGreaterThan(10);

      // Verify bounds
      const lineCount = sample.code.split('\n').length;
      const byteSize = new Blob([sample.code]).size;

      expect(lineCount).toBeLessThanOrEqual(500);
      expect(byteSize).toBeLessThanOrEqual(65536);
    }
  });

  test('security vulnerable sample contains eval and shell signals', () => {
    const secSample = CODE_SAMPLES.find((s) => s.id === 'security_vulnerable');
    expect(secSample).toBeDefined();
    expect(secSample?.code).toContain('eval(');
    expect(secSample?.code).toContain('os.system(');
  });
});
