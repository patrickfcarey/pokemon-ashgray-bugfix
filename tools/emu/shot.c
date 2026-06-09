/* Headless mGBA screenshot harness: load ROM via VFile, run N frames, dump framebuffer. */
#include <mgba/core/core.h>
#include <mgba/core/log.h>
#include <mgba/gba/core.h>
#include <mgba-util/vfs.h>
#include <fcntl.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>

/* path-based VFS open is guarded in the header but exported by the lib */
struct VFile* VFileOpen(const char* path, int flags);
static void noLog(struct mLogger* l, int c, enum mLogLevel lv, const char* f, va_list a) {
	(void) l; (void) c; (void) lv; (void) f; (void) a;
}
static struct mLogger silentLogger = { .log = noLog };

int main(int argc, char** argv) {
	setbuf(stderr, NULL);
	mLogSetDefaultLogger(&silentLogger);
	if (argc < 2) { fprintf(stderr, "usage: shot rom [frames] [out.raw]\n"); return 1; }
	const char* rom = argv[1];
	int frames = argc > 2 ? atoi(argv[2]) : 200;
	const char* out = argc > 3 ? argv[3] : "frame.raw";

	struct VFile* vf = VFileOpen(rom, O_RDONLY);
	if (!vf) { fprintf(stderr, "VFileOpen failed\n"); return 2; }
	struct mCore* core = GBACoreCreate();
	if (!core) { fprintf(stderr, "GBACoreCreate failed\n"); return 3; }
	core->init(core);
	fprintf(stderr, "init ok\n");
	mCoreInitConfig(core, NULL);
	if (!core->loadROM(core, vf)) { fprintf(stderr, "loadROM failed\n"); return 4; }
	fprintf(stderr, "loadROM ok\n");

	unsigned w, h;
	core->baseVideoSize(core, &w, &h);
	mColor* buf = malloc((size_t) w * h * sizeof(mColor));
	core->setVideoBuffer(core, buf, w);
	fprintf(stderr, "video %ux%u set\n", w, h);

	core->reset(core);
	fprintf(stderr, "reset ok; running %d frames\n", frames);
	for (int i = 0; i < frames; i++) core->runFrame(core);
	fprintf(stderr, "frames done\n");

	FILE* f = fopen(out, "wb");
	fwrite(buf, sizeof(mColor), (size_t) w * h, f);
	fclose(f);
	fprintf(stderr, "ok %ux%u frames=%d bytes/px=%zu -> %s\n", w, h, frames, sizeof(mColor), out);
	printf("%u %u\n", w, h);
	return 0;
}
