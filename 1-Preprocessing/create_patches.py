import os
import argparse
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from WholeSlideImage import WholeSlideImage


def init_df(args):
    image_extensions = ['.tif', '.tiff', '.svs', '.mrxs', '.ndpi']
    filenames = [f.name for f in Path(args.src).rglob('*') if f.suffix in image_extensions]
    status = ['tbp'] * len(filenames)
    process = [''] * len(filenames)
    df = pd.DataFrame({'slide_id': filenames, 'status': status, 'process': process})
    return df


def main(args):
    os.makedirs(args.dst, exist_ok=True)
    df_path = os.path.join(args.dst, 'status.csv')
    df = init_df(args)
    df.to_csv(df_path, index=False)
    for i in tqdm(range(df.shape[0])):
        slide_id = df.loc[i, 'slide_id']
        print(f'Processing {slide_id}...')
        slide_path = os.path.join(args.src, slide_id)
        os.makedirs(args.dst, exist_ok=True)
        try:
            wsi = WholeSlideImage(slide_path, args.dst, patch_size=args.patch_size, base_downsample=args.base_downsample,
                                  downsample_factor=args.downsample_factor, num_levels=args.num_levels, use_otsu=not args.no_use_otsu,
                                  sthresh=args.sthresh, sthresh_up=args.sthresh_up, mthresh=args.mthresh, padding=not args.no_padding,
                                  visualize=not args.no_visualize, visualize_width=args.visualize_width, skip=not args.no_skip)
            wsi.multi_level_segment()
            df.loc[i, 'status'] = 'done'
        except Exception as e:
            print(f'Error processing {slide_id} of subtype!!!')
            print(e)
            df.loc[i, 'status'] = 'error'
        df.to_csv(df_path, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Whole Slide Image Processing')
    parser.add_argument('--src', type=str, default='/vast/palmer/scratch/liu_xiaofeng/li/CAMELYON16')
    parser.add_argument('--dst', type=str, default='/vast/palmer/scratch/liu_xiaofeng/li/patches_CAMELYON16')
    parser.add_argument('--patch_size', type=int, default=512)
    parser.add_argument('--base_downsample', type=int, default=1)
    parser.add_argument('--downsample_factor', type=int, default=4)
    parser.add_argument('--num_levels', type=int, default=3)
    parser.add_argument('--no_use_otsu', action='store_true')
    parser.add_argument('--sthresh', type=int, default=20)
    parser.add_argument('--sthresh_up', type=int, default=255)
    parser.add_argument('--mthresh', type=int, default=7)
    parser.add_argument('--no_padding', action='store_true')
    parser.add_argument('--no_visualize', action='store_true')
    parser.add_argument('--visualize_width', type=int, default=1024)
    parser.add_argument('--no_skip', action='store_true')
    args = parser.parse_args()
    main(args)